from django.shortcuts import get_object_or_404, render
from rest_framework import status
from django.contrib import messages
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from backend.models.allmodels import (
    Course,
    CourseRegisterRecord,
    CourseEnrollment,
    Progress,
    Quiz,
    Question,
    QuizAttemptHistory
)
from django.views.generic import (
    DetailView,
    ListView,
    TemplateView,
    FormView,
    CreateView,
    FormView,
    UpdateView,
)
from backend.forms import (
    QuestionForm,
)
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.decorators import method_decorator

from backend.serializers.enrollcourseserializers import (
    AssignCourseEnrollmentSerializer, 
    CourseEnrollmentSerializer, 
    RegisteredCourseSerializer, 
    UnAssignCourseEnrollmentSerializer, 
    UserSerializer
)
from backend.models.coremodels import *

# for enrollment feature
# will be displayed to employer/client-admin only

# [similar view is in courseviews.py]
class RegisteredCourseListView(APIView):
    """
    view to display data about list of courses on which customer is registered to use.
    trigger with GET request
    should be allowed for only [Employer].
    
    table : Course, CourseRegisterRecord
    what will be displayed:
                    list course.id, course.title [course_id to be retrieved from CourseRegisterRecord]
    """
    '''
        what will happen:
                    user will be extracted from request
                    user's customer_id will be retrieved then
                    CourseRegisterRecord will be filtered on the basis of this customer_id
                    and list of course_ids will be made
                    list of course_ids will be used to retrieve the list of course titles associated with it from course table.
    '''
    def get(self, request, format=None):
        try:
                        # ********************************
            # =================================================================
            user_header = request.headers.get("user")
            if user_header:
                user_data = json.loads(user_header)
                customer_id = user_data.get("customer")
            # =================================================================
            # # Get the customer ID from the request user
            # customer_id = request.user.customer.id
        except AttributeError:
            # Handle cases where the user might not have an associated customer
            return Response({"error": "No associated customer found for user."}, status=status.HTTP_404_NOT_FOUND)

        # Filter CourseRegisterRecord based on customer ID to get the list of course IDs
        registered_courses_ids = CourseRegisterRecord.objects.filter(customer_id=customer_id).values_list('course_id', flat=True)

        if not registered_courses_ids:
            # If no registered courses are found, return a 404
            return Response({"error": "No registered courses found for the given customer."}, status=status.HTTP_404_NOT_FOUND)

        # Get the list of courses based on the course IDs
        courses = Course.objects.filter(id__in=registered_courses_ids)
        
        if not courses.exists():
            # If no courses are found with the given IDs (shouldn't happen, but good to check)
            return Response({"error": "No courses found."}, status=status.HTTP_404_NOT_FOUND)

        # Serialize the course data
        serializer = RegisteredCourseSerializer(courses, many=True)

        return Response(serializer.data)

class UserListForEnrollment(APIView):
    """
    view to display data about list of user which have customer id same as that of user in request.
    trigger with GET request
    should be allowed for only [Employer].
    
    table : User
    what will be displayed:
                    id, first_name, last_name, status
                    
    """
    '''
        what will happen:
                    user will be extracted from request
                    user's customer_id will be retrieved then
                    CourseRegisterRecord will be filtered on the basis of this customer_id
                    and list of course_ids will be made
                    list of course_ids will be used to retrieve the list of course titles associated with it from course table.
    '''
    def get(self, request):
            # =================================================================
        user_header = request.headers.get("user")
        if user_header:
            user_data = json.loads(user_header)
            customer_id = user_data.get("customer")
            # =================================================================
        # # Extract user from the request
        # user = request.user

        # # Retrieve the customer_id from the user
        # customer_id = user.customer_id

        # Filter User objects based on the customer_id
        users = User.objects.filter(customer_id=customer_id)

        # Serialize the user data
        serialized_users = UserSerializer(users, many=True)

        return Response(serialized_users.data)

class CreateCourseEnrollmentView(APIView):
    """
        view to create instances in CourseEnrollment.
        trigger with POST request
        should be allowed for only [Employer].
        
        table : CourseEnrollment
        
        in request body :
                        list of course_id =[..., ..., ..., ...]
                        list of user_id =[..., ..., ..., ...]
        in response body :
                        each course in list will be mapped for all users in list inside CourseEnrollment table
                        by default active will be true
    """
    pass

class DisplayCourseEnrollmentView(APIView):
    """
        view to display all instances of CourseEnrollment Table.
        trigger with GET request
        
        table : CourseEnrollment, User , Course
        
        what will be displayed:
                    id
                    course.title,
                    user.first_name,
                    user.last_name,
                    enrolled_at,
                    active
    """
    pass

class UnAssignCourseEnrollmentView(APIView):
    """
    this API is used to unassign course to specified user(s) by turning the active false , and hide visibility of course to user(s).
    required inputs : list of ids of instance of course enrollment table
    
    Method: POST
    Parameters:
        - enrollment_ids (list of integers): IDs of course enrollment instances to unassign.
    
    It is triggered with POST request.
    
    """
    def post(self, request, *args, **kwargs):
        try:
            # Deserialize and validate the input data
            serializer = UnAssignCourseEnrollmentSerializer(data=request.data)
            if serializer.is_valid():
                enrollment_ids = serializer.validated_data.get('enrollment_ids')
                # Check if any enrollment IDs were provided
                if not enrollment_ids:
                    return Response({'error': 'No enrollment IDs provided'}, status=status.HTTP_400_BAD_REQUEST)

                # Check if all provided enrollment IDs are integers
                invalid_ids = [id for id in enrollment_ids if not isinstance(id, int)]
                if invalid_ids:
                    return Response({'error': 'Invalid enrollment IDs provided'}, status=status.HTTP_400_BAD_REQUEST)

                # Check if any provided enrollment IDs are not found in the database
                enrollments = CourseEnrollment.objects.filter(id__in=enrollment_ids)
                if len(enrollments) != len(enrollment_ids):
                    return Response({'error': 'One or more enrollment IDs do not exist'}, status=status.HTTP_404_NOT_FOUND)

                # Update active status to False for the specified enrollments
                updated_count = enrollments.update(active=False)

                if updated_count > 0:
                    return Response({'message': f'Courses unassigned successfully. {updated_count} enrollments updated.'}, status=status.HTTP_200_OK)
                else:
                    return Response({'error': 'None of the provided enrollment IDs are active'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
class AssignCourseEnrollmentView(APIView):
    """
    this API is used to assign course to specified user(s) for all users in courseenrollment table who have active false
    in request body : list of ids of instance of course enrollment table
    
    Method: POST
    Parameters:
        - enrollment_ids (list of integers): IDs of course enrollment instances to assign, who have active status false for now
    
    It is triggered with POST request.
    
    """
    def post(self, request, *args, **kwargs):
        serializer = AssignCourseEnrollmentSerializer(data=request.data)
        try:
            if serializer.is_valid():
                enrollment_ids = serializer.validated_data.get('enrollment_ids', [])

                # Validate input
                if not enrollment_ids:
                    return Response({'error': 'No enrollment IDs provided'}, status=status.HTTP_400_BAD_REQUEST)

                # Attempt to update active status to True for the specified enrollments
                # Filter for enrollments that are inactive and match the provided IDs
                enrollments_to_update = CourseEnrollment.objects.filter(id__in=enrollment_ids, active=False)

                # Check if there are actually enrollments to update
                if not enrollments_to_update.exists():
                    return Response({'error': 'No valid enrollments found to update. They may not exist or are already active.'}, status=status.HTTP_404_NOT_FOUND)

                # If there are enrollments to update, proceed with the update
                updated_count = enrollments_to_update.update(active=True)

                # Optionally, check if the updated count matches the expected number of IDs provided (if needed)
                # This is an additional step to provide more detailed feedback
                if updated_count != len(enrollment_ids):
                    return Response({'warning': 'Some enrollments were not updated because they did not exist or were already active.',
                                    'updated_count': updated_count}, status=status.HTTP_206_PARTIAL_CONTENT)

                return Response({'message': 'Course(s) assigned successfully', 'updated_count': updated_count}, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)