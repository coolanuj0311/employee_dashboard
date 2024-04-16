import json
from django.views import View
import pandas as pd
import requests
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.utils import timezone
from django.utils.decorators import method_decorator
from rest_framework import generics, status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
#custom_authentication in main model is "core"
# from core.custom_mixins import (
from custom_authentication.custom_mixins import ClientAdminMixin, ClientMixin, SuperAdminMixin
#exam in main model "backend"
# from backend.models.allmodels import(
from exam.models.allmodels import (
    CourseCompletionStatusPerUser,
    CourseEnrollment,
    CourseStructure,
    Quiz,
    QuizAttemptHistory,
    QuizScore,
)

class CreateCourseCompletionStatusPerUserView(ClientAdminMixin, APIView):
    """
    allowed for client admin
    POST request
    triggered after course enrollment records creation, similar to that one.
    in request body:
        list of course_id =[..., ..., ..., ...]
        list of user_id =[..., ..., ..., ...]
        each course in list will be mapped for all users in list
    while creating instance:
        enrolled_user = request body
        course = request body
        completion_status = (default=False)
        in_progress_status = (default=False)
        created_at = (auto_now_add=True)
       
    """
    def post(self, request):
        try:
            # Check if the user has client admin privileges
            if not self.has_client_admin_privileges(request):
                return JsonResponse({"error": "You do not have permission to access this resource"}, status=403)
            
        
            course_ids = request.data.get('course_id', [])
            user_ids = request.data.get('user_id', [])

            # Validate request data
            if not course_ids or not user_ids:
                return Response({'error': 'course_id and user_id lists are required'}, status=status.HTTP_400_BAD_REQUEST)

            # Additional validation
            if not all(isinstance(course_id, int) for course_id in course_ids):
                return Response({'error': 'Invalid course_id format'}, status=status.HTTP_400_BAD_REQUEST)
            if not all(isinstance(user_id, int) for user_id in user_ids):
                return Response({'error': 'Invalid user_id format'}, status=status.HTTP_400_BAD_REQUEST)

            # Create course completion status records only if they don't already exist
            course_completion_statuses = []
            for course_id in course_ids:
                for user_id in user_ids:
                    # Check if a record already exists for this combination
                    if not CourseCompletionStatusPerUser.objects.filter(Q(course_id=course_id) & Q(enrolled_user_id=user_id)).exists():
                        # Create a new record only if it doesn't exist
                        course_completion_status = CourseCompletionStatusPerUser(
                            enrolled_user_id=user_id,
                            course_id=course_id,
                            completion_status=False,
                            in_progress_status=False
                        )
                        course_completion_statuses.append(course_completion_status)

            # Save course completion status records to the database
            CourseCompletionStatusPerUser.objects.bulk_create(course_completion_statuses)

            return Response({'message': 'Course completion statuses created successfully'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    
class UpdateCompleteQuizCountView(ClientAdminMixin, APIView):
    """
    POST request triggered when quiz attempt history for that course, that user have completed = true,
    if set of quiz, course, user doesn't already have completed = true in table
    while updating instance:
        completed_quiz_count = increment by 1
    """

    def post(self, request):
        try:
            # Check if the user has client admin privileges
            if not self.has_client_admin_privileges(request):
                return JsonResponse({"error": "You do not have permission to access this resource"}, status=403)

            course_id = request.data.get('course_id')
            user_id = request.data.get('user_id')

            # Validate request data
            if not (course_id and user_id):
                return Response({'error': 'course_id and user_id are required'}, status=status.HTTP_400_BAD_REQUEST)

            # Get distinct completed quizzes for the user and course
            completed_quizzes = QuizAttemptHistory.objects.filter(course_id=course_id, enrolled_user_id=user_id, complete=True).values('quiz_id').distinct().first()

            # Ensure at least one completed quiz is found
            if completed_quizzes:
                # Initialize a set to keep track of counted quiz IDs
                counted_quiz_ids = set()

                # Check if the completed_quizzes is not None
                if 'quiz_id' in completed_quizzes:
                    # Extract the quiz_id
                    quiz_id = completed_quizzes['quiz_id']

                    # Check if the quiz ID has already been counted
                    if quiz_id not in counted_quiz_ids:
                        # Update completed_quiz_count for the corresponding record
                        quiz_score, created = QuizScore.objects.get_or_create(
                            course_id=course_id,
                            enrolled_user_id=user_id,
                            defaults={'completed_quiz_count': 0}
                        )

                        # Increment completed_quiz_count by 1
                        quiz_score.completed_quiz_count += 1
                        quiz_score.save()

                        # Add the quiz_id to the set of counted quiz IDs
                        counted_quiz_ids.add(quiz_id)

                return Response({'message': 'Completed quiz count updated successfully'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'No completed quizzes found for the user and course'}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        

class CreateQuizScoreView(ClientAdminMixin,APIView):
    """
    allowed for client admin
    POST request
    triggered after course enrollment records creation, similar to that one.
    in request body:
        list of course_id =[..., ..., ..., ...]
        list of user_id =[..., ..., ..., ...]
        each course in list will be mapped for all users in list
    while creating instance:
        enrolled_user = request body
        course = request body
        total_quizzes_per_course = calculate in view for course by counting active quizzes in it
        completed_quiz_count = by default 0
        total_score_per_course = (default=0)
    """
    def post(self, request):
        try:
            # Check if the user has client admin privileges
            if not self.has_client_admin_privileges(request):
                return JsonResponse({"error": "You do not have permission to access this resource"}, status=403)
            course_ids = request.data.get('course_id', [])
            user_ids = request.data.get('user_id', [])

            # Validate request data
            if not course_ids or not user_ids:
                return Response({'error': 'course_id and user_id lists are required'}, status=status.HTTP_400_BAD_REQUEST)

            # Create quiz score records
            quiz_scores = []
            for course_id in course_ids:
                # Calculate total quizzes for the course
                total_quizzes_per_course = self.get_total_quizzes_per_course(course_id)

                for user_id in user_ids:
                    # Check if QuizScore instance already exists for this user and course
                    existing_score = QuizScore.objects.filter(course_id=course_id, enrolled_user_id=user_id).first()

                    if existing_score:
                        continue  # Skip creation if QuizScore instance already exists

                    # Create new QuizScore instance
                    quiz_score = QuizScore(
                        enrolled_user_id=user_id,
                        course_id=course_id,
                        total_quizzes_per_course=total_quizzes_per_course,
                        completed_quiz_count=0,
                        total_score_per_course=0,
                        created_at=timezone.now(),
                        updated_at=timezone.now(),
                        active=True
                    )
                    quiz_scores.append(quiz_score)

            # Save quiz score records to the database
            QuizScore.objects.bulk_create(quiz_scores)

            return Response({'message': 'Quiz scores created successfully'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_total_quizzes_per_course(self, course_id):
        try:
        # Count the number of quizzes associated with the given course_id
            total_quizzes = CourseStructure.objects.filter(course_id=course_id, content_type='quiz', active=True).count()
            return total_quizzes
        except Exception as e:
        # Handle exceptions if any
          return 0  # Return 0 in case of error


class UpdateTotalScorePerCourseView(ClientAdminMixin,APIView):
    """
    POST request
    triggered when quiz attempt history for that course, that user have completed = true 
    while updating instance:
        total_score_per_course -> calculate for it 
        score=current_score/question_list_order.split().count()
    """
    def post(self, request):
        try:
            # Check if the user has client admin privileges
            if not self.has_client_admin_privileges(request):
                return JsonResponse({"error": "You do not have permission to access this resource"}, status=403)
            course_id = request.data.get('course_id')
            user_id = request.data.get('user_id')

            # Validate request data
            if not (course_id and user_id):
                return Response({'error': 'course_id and user_id are required'}, status=status.HTTP_400_BAD_REQUEST)

            # Get unique instances of completed quizzes for the user and course
            
            from django.db.models import Max

            last_attempted_quizzes = (
                QuizAttemptHistory.objects.filter(course_id=course_id, enrolled_user_id=user_id, complete=True)
                .values('quiz_id')
                .annotate(last_attempt=Max('created_at'))
                .order_by('-last_attempt')
            )

            unique_quizzes = QuizAttemptHistory.objects.filter(
                course_id=course_id,
                enrolled_user_id=user_id,
                complete=True,
                created_at__in=[quiz['last_attempt'] for quiz in last_attempted_quizzes]
            )

            # Calculate total score for the user and course
            total_score = 0
            for quiz_attempt in unique_quizzes:
                total_score += (quiz_attempt.current_score / (len(quiz_attempt.question_list_order.split(','))-1))


            # Get total quizzes for the course
            total_quizzes = QuizScore.objects.get(course_id=course_id, enrolled_user_id=user_id).total_quizzes_per_course
           

            # Calculate average score
            if total_quizzes > 0:
                average_score = (total_score / total_quizzes) * 100
            else:
                average_score = 0

            # Update total_score_per_course for the corresponding record
            quiz_score, created = QuizScore.objects.get_or_create(course_id=course_id, enrolled_user_id=user_id, defaults={'total_score_per_course': 0})
            quiz_score.total_score_per_course = average_score
            quiz_score.save()

            return Response({'message': 'Total score per course updated successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UpdateCourseCompletionStatusPerUserView(ClientAdminMixin,APIView):

    """
    POST request
    triggers when 
    total_quizzes_per_course = completed_quiz_count in quiz score for that user in request
    if total_quizzes_per_course == completed_quiz_count:
        completion_status=True and in_progress_status =False
    if total_quizzes_per_course > completed_quiz_count:
        completion_status=False and in_progress_status =True
        
    """
    @transaction.atomic
    def post(self, request):
        try:
            # Check if the user has client admin privileges
            if not self.has_client_admin_privileges(request):
                return JsonResponse({"error": "You do not have permission to access this resource"}, status=403)
            course_id = request.data.get('course_id')
            user_id = request.data.get('user_id')

            # Validate request data
            if not (course_id and user_id):
                return Response({'error': 'course_id and user_id are required'}, status=status.HTTP_400_BAD_REQUEST)

            # Retrieve or create CourseCompletionStatus record
            course_completion_status, created = CourseCompletionStatusPerUser.objects.get_or_create(
                course_id=course_id, enrolled_user_id=user_id
            )

            # Retrieve quiz score record for the user and course
            quiz_score = get_object_or_404(QuizScore, course_id=course_id, enrolled_user_id=user_id)

            # Update completion status
            if quiz_score.total_quizzes_per_course == quiz_score.completed_quiz_count:
                course_completion_status.completion_status = True
                course_completion_status.in_progress_status = False
            elif quiz_score.total_quizzes_per_course > quiz_score.completed_quiz_count:
                course_completion_status.completion_status = False
                course_completion_status.in_progress_status = True

            # Save the updated CourseCompletionStatus record
            course_completion_status.save()

            return Response({'message': 'Course completion status updated successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            if isinstance(e, QuizScore.DoesNotExist):
                return Response({'error': 'Quiz score record not found'}, status=status.HTTP_404_NOT_FOUND)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DisplayClientCourseProgressView(ClientMixin,APIView):

    """
    GET request
    for user in request, if he has data in course enrollment table
    display if the user in request has active enrollment for the course
    display:
        completed_quiz_count
    """

    def get(self, request):
        try:
            # # Check if the user has client admin privileges
            if not self.has_client_privileges(request):
                return JsonResponse({"error": "You do not have permission to access this resource"}, status=403)
            user_id = request.query_params.get('user_id')

            # Validate request data
            if not user_id:
                return Response({'error': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)

            # Check if the user has active enrollment for any course
            course_enrollments = CourseEnrollment.objects.filter(user_id=user_id, active=True)

            if not course_enrollments:
                return Response({'message': 'No active enrollment found for the user'}, status=status.HTTP_404_NOT_FOUND)

            # Display course progress for each active enrollment
            progress_data = []
            for enrollment in course_enrollments:
                quiz_score = QuizScore.objects.filter(course_id=enrollment.course_id, enrolled_user_id=user_id).first()
                if quiz_score:
                   
                    progress_percentage = 0
                    total_quiz_count = quiz_score.total_quizzes_per_course
                    completed_quiz_count = quiz_score.completed_quiz_count

                    # Determine completion_status or in_progress_status based on completed quiz count
                    if total_quiz_count == completed_quiz_count:
                        completion_status = True
                        in_progress_status = False
                    elif completed_quiz_count == 0:
                        completion_status = False
                        in_progress_status = False
                    else:
                        completion_status = False
                        in_progress_status = True
                    if quiz_score.total_quizzes_per_course > 0:
                        progress_percentage = (quiz_score.completed_quiz_count / quiz_score.total_quizzes_per_course) * 100
                    
                    progress_data.append({
                        'course_id': enrollment.course_id,
                        'course_name': enrollment.course.title,
                        'completed_quiz_count': quiz_score.completed_quiz_count,
                        'total_quizzes_per_course': quiz_score.total_quizzes_per_course,
                        'progress_percentage': progress_percentage,
                         'completion_status': completion_status,
                        'in_progress_status': in_progress_status
                    })

            return Response({'progress': progress_data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CountCoursesStatusView(ClientMixin,APIView):
    """
    GET request to count the number of active enrollments and course completion status for a user.
    """

    def get(self, request):
        try:
            # Check if the user has client admin privileges
            if not self.has_client_privileges(request):
                return JsonResponse({"error": "You do not have permission to access this resource"}, status=403)
            user_id = request.query_params.get('user_id')
            if not user_id:
                return Response({'error': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)

            # Count active enrollments for the user
            active_enrollments_count = CourseEnrollment.objects.filter(user_id=user_id, active=True).count()

            # Count completed, in-progress, and not started courses
            completed_courses_count = CourseCompletionStatusPerUser.objects.filter(enrolled_user_id=user_id, completion_status=True, in_progress_status=False).count()
            in_progress_courses_count = CourseCompletionStatusPerUser.objects.filter(enrolled_user_id=user_id, completion_status=False, in_progress_status=True).count()
            not_started_courses_count = CourseCompletionStatusPerUser.objects.filter(enrolled_user_id=user_id, completion_status=False, in_progress_status=False).count()

            return Response({
                'active_enrollments_count': active_enrollments_count,
                'completed_courses_count': completed_courses_count,
                'in_progress_courses_count': in_progress_courses_count,
                'not_started_courses_count': not_started_courses_count
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# #for front end integration
# class EmployeeDashboard(View):
#     template_name = 'employee.html'
#     error_template_name = 'error.html'
#     completed_courses_api_url = 'http://127.0.0.1:8000/count-courses-status'
#     course_progress_api_url = 'http://127.0.0.1:8000/display-client-course-progress/'

#     def get(self, request):
#         user_id = request.GET.get('user_id')
#         if not user_id:
#             return render(request, self.error_template_name, {'error': 'user_id is required'})

#         # Make request to count-client-completed-courses API
#         completed_courses_response = requests.get(self.completed_courses_api_url, params={'user_id': user_id})
#         if completed_courses_response.status_code == 200:
#             completed_courses_data = completed_courses_response.json()
#         else:
#             return render(request, self.error_template_name, {'error': 'Failed to fetch data from completed courses API'})

#         # Make request to display-client-course-progress API
#         course_progress_response = requests.get(self.course_progress_api_url, params={'user_id': user_id})
#         if course_progress_response.status_code == 200:
#             course_progress_data = course_progress_response.json().get('progress', [])
#         else:
#             return render(request, self.error_template_name, {'error': 'Failed to fetch data from course progress API'})

#         # Extracting relevant data from the responses
#         completed_courses_count = completed_courses_data.get('completed_courses_count', 0)
#         in_progress_courses_count = completed_courses_data.get('in_progress_courses_count', 0)
#         not_started_courses_count = completed_courses_data.get('not_started_courses_count', 0)
#         course_names = [entry.get('course_name', '') for entry in course_progress_data]
#         progress_percentages = [entry.get('progress_percentage', 0) for entry in course_progress_data]

#         return render(request, self.template_name, {
#             'completed_courses_count': completed_courses_count,
#             'in_progress_courses_count': in_progress_courses_count,
#             'not_started_courses_count': not_started_courses_count,
#             'course_names': course_names,
#             'progress_percentages': progress_percentages
#         })


# =================================================================
# employer dashboard
# =================================================================

class ActiveEnrolledUserCountPerCustomerView(APIView):
    """get api
    for client admin (count per customer id of user in request)
    """
    pass

class RegisteredCourseCountView(APIView):
    """get api
    for client admin (count per customer id of user in request)
    """
    pass

#---------
# graph : (per course)(for a customer) [employeer (client admin) dashboard]
class CountOfCompletionPerRegisteredCourseView(APIView):
    """_summary_

    Args:
        APIView (_type_): _description_
    """
    pass

class CountOfInProgressPerRegisteredCourseView(APIView):
    """_summary_

    Args:
        APIView (_type_): _description_
    """
    pass

class CountOfNotStartedPerRegisteredCourseView(APIView):
    """_summary_

    Args:
        APIView (_type_): _description_
    """
    pass
#---------

# =================================================================
# super admin dashboard
# =================================================================

class ActiveCourseCountView(APIView):
    """get api
    for super admin
    """
    pass

class InActiveCourseCountView(APIView):
    """get api
    for super admin
    """
    pass

class ActiveRegisteredCustomerCountView(APIView):
    """get api
    for super admin
    """
    pass

# ----
# graph : (only per course) [ (super admin) dashboard]

class CountOfCompletionPerCourseView(APIView):
    """_summary_

    Args:
        APIView (_type_): _description_
    """
    pass

class CountOfInProgressPerCourseView(APIView):
    """_summary_

    Args:
        APIView (_type_): _description_
    """
    pass

class CountOfNotStartedPerCourseView(APIView):
    """_summary_

    Args:
        APIView (_type_): _description_
    """
    pass
# ----

# graph to count registrations per course 
class CountOfActiveRegistrationPerCoure(APIView):
    pass