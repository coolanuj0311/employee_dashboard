from django.shortcuts import render
from rest_framework import status

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from .models import (
    # User,
    Course,
    Customer,
    CourseRegisterRecord,
    CourseEnrollment,
)
from .serializers import (
    CostumerDisplaySerializer,
    CourseDisplaySerializer,
)


# Create your views here.

# class CourseDisplayView(APIView):
    
#     def get(self, request):
#         # Retrieve all courses from the database
#         courses = Course.objects.all()

#         # Serialize the queryset
#         serializer = CourseSerializer(courses, many=True)

#         # Return serialized data in the response
#         return Response(serializer.data)


#for course registration page
class ActiveCourseListView(generics.ListAPIView):
    """
    this API is used to retrieve data from course table regarding all courses which are active to be used.
    it is triggered with GET request.
    
    to be used for registering the courses.
    """
    queryset = Course.objects.filter(active=True)
    serializer_class = CourseDisplaySerializer
    permission_classes = [IsAuthenticated]

class CostumerListView(generics.ListAPIView):
    """
    this API is used to retrieve data especially names from costumer table.
    it is triggered with GET request.
    """
    '''
        TODO :need to understand if there is costumer_role_privilege type of thing and get what resource privileges they might have.
    '''
    # queryset = Costumer.objects.all() # may use filter with help of role if they are assigned any to , especially that they can use lms
    # serializer_class = CostumerDisplaySerializer
    # permission_classes = [IsAuthenticated]
    pass
    
class CreateCourseRegisterRecordView(APIView):
    
    def post(self, request, *args, **kwargs):
        # Retrieve customer IDs and course IDs from request data
        course_ids = request.data.get('course_ids', [])
        customer_ids = request.data.get('customer_ids', [])
        
        
        # Validate request data
        if not course_ids:
            return Response({'error': 'Course IDs are missing'}, status=status.HTTP_400_BAD_REQUEST)
        if not customer_ids:
            return Response({'error': 'Customer IDs are missing'}, status=status.HTTP_400_BAD_REQUEST)
        
        
        # Iterate over each course
        for course_id in course_ids:
            course = Course.objects.filter(pk=course_id).first()
            if not course:
                return Response({'error': f'Course with ID {course_id} does not exist'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Iterate over each customer
            for customer_id in customer_ids:
                customer = Customer.objects.filter(pk=customer_id).first()
                if not customer:
                    return Response({'error': f'Customer with ID {customer_id} does not exist'}, status=status.HTTP_400_BAD_REQUEST)
                
                # Create CourseRegisterRecord
                CourseRegisterRecord.objects.create(customer=customer, course=course)

        return Response({'message': 'Course registration records created successfully'}, status=status.HTTP_201_CREATED)

# TODO: make api for coursesalesrecordtable -display , update like course enrollment table

#for course enrollment page
class ClientAdminCourseListView(APIView):
    """
    this API is used to retrieve course which are allocated or register under client admin's company, which will be retrieved from user's customer id.
    it is triggered with GET request.
    """
    # permission_classes = [IsAuthenticated]

    def get(self,request, *args, **kwargs):
        pass


class ClientAdminEmployeeListView(APIView):
    """
    this API is used to retrieve list of employees which have same costumer id as client-admin himself(current logged in user).
    it is triggered with GET request.
    """
    # permission_classes = [IsAuthenticated]

    def get (self,request, *args, **kwargs):
        pass

# class AssignCourseEnrollmentView(APIView):
#     """
#     this API is used to create new records in course enrollment table by assigning the course(s) to user(s) and and enable visibility of course to user(s).    required inputs : list of courses and list of users
    
#     Method: POST
#     Parameters:
#         - courses (list of integers): IDs of courses to assign.
#         - users (list of integers): IDs of users to assign the courses.
    
#     It is triggered with POST request.
    
#     """
#     def post (self,request, *args, **kwargs):
#         pass

# class UnAssignCourseEnrollmentView(APIView):
#     """
#     this API is used to unassign course to specified user(s) by turning the active false , and hide visibility of course to user(s).
#     required inputs : list of ids of instance of course enrollment table
    
#     Method: POST
#     Parameters:
#         - enrollment_ids (list of integers): IDs of course enrollment instances to unassign.
    
#     It is triggered with POST request.
    
#     """
#     def post(self,request, *args, **kwargs):
#         pass

class CourseEnrollmentDisplayView(generics.ListAPIView):
    """
    this API i used to display the course enrollment table's instance record, of it's company's employees.
    it is triggered with GET request.
    """
    # def get_queryset(self):
    #     # Extract the customer ID associated with the logged-in user
    #     customer_id = self.request.user.customer_id  # Adjust this according to your user model

    #     # Query the course enrollment table to retrieve users with the same customer ID
    #     employees = User.objects.filter(customer_id=customer_id)  # Adjust this according to your user model

    #     # Retrieve course enrollments for the filtered employees
    #     queryset = CourseEnrollment.objects.filter(user__in=employees)

    #     return queryset
    pass

class CourseListView(generics.ListAPIView):
    """
    to display all courses present in the database
    it is triggered with GET request.
    """
    queryset = Course.objects.all()
    serializer_class = CourseDisplaySerializer
    permission_classes = [IsAuthenticated]

# ===============================================================
        # creating course for first time views    
# ===============================================================

# for create new course button
class CreateCourseView(APIView):
    """
        view to used for creating a course instance.
        triggers with POST request.
        i/p- title , summary in request body
        table : Course
        while creating instance :
                    slug = auto generated by pre_save()
                    title = request body
                    summary = request body
                    created_at = updated_at = models.DateTimeField(auto_now=True)
                    active = False
                    original_course = null (as it is original course itself)
        and instance is saved
    """
    pass

class CreateCourseSectionView(APIView):
    """
        view to create a section in course.
        triggers with POST request.
        in URL : course id will be passed in which this section is being created
        table : Section
        while creating instance :
                    course = id from url
                    title = request body
                    section_number = request body [to be used for ordering how content inside course will look]
        and instance is saved
    """
    pass

class CreateReadingMaterialView(APIView):
    """
        view to create reading material inside a course.
        triggers with POST request.
        in URL : course_id and section_id in which we are inputing the content will be passed
        table : UploadReadingMaterial
        while creating instance :
                    title = request body
                    course = id in url
                    reading_content = request body
                    uploaded_at = updated_at = models.DateTimeField(auto_now=True, auto_now_add=False, null=True)
        and instance is saved
    """
    pass

class CreateVideoView(APIView):
    """
        view to create video inside a course.
        triggers with POST request.
        in URL : course_id and section_id in which we are inputting the content will be passed
        table :  UploadVideo
        while creating instance :
                    slug = auto generated by pre_save
                    course = id in url
                    video = request body
                    summary = request body
                    uploaded_at = auto now
    """
    pass

class CreateQuizView(APIView):
    """
        view to create quiz inside a course.
        triggers with POST request.
        in URL : course_id and section_id in which we are inputting the content will be passed
        table : Quiz
        while creating instance :
                    course = id in url
                    title = request body
                    slug = auto generated by pre_save
                    random_order = request body
                    answers_at_end = request body
                    exam_paper = t/f from request body
                    pass_mark = request body
                    created_at = updated_at = models.DateField(auto_now=True)
                    active = False by default
    """
    pass


# should be triggered after create quiz
class CreateQuestion(APIView):
    """
        view to create the instance of question inside quiz
        triggers with POST request.
        in URL : course_id and section_id in which we are inputting the content will be passed
        while creating instance :
                    figure = request body
                    content = request body
                    explanation = request body
                    choice_order = request body
                    active = false by default
    """
    pass

# should be triggered in question is created and is saved , inside the form for the quiz creation
class CreateQuizQuestion(APIView):
    """
        # should be triggered simultaneously with question creation inside a quiz
        view to create instance in quiz question model , in order to related question with the quiz.
        triggers with POST request.
        in URL : quiz_id and question_id in which we are inputting the content will be passed
        while creating instance :
                    quiz = id in url
                    question = id in url
                    # Additional fields specific to the relationship
                    active = true by default
    """
    pass

# might not be needed like in lms what we are taking as exemplary where it is feed via form submission
class CreateChoiceView(APIView):
    """
        view to create choices in choice model for question
        triggers with POST request
        in URL : quiz_id and question_id in which we are inputting the content will be passed.
        while creating instance :
                    question = id in url
                    choice = request body
                    correct = request body
    """
    pass


# will be triggered when after selecting the type of content content is saved in it's respective table
class CreateCourseSectionContent(APIView):
    """
        view to create content for the section inside a course
        trigger with POST request
        in URL : course_id and section_id and content_id in which we are inputting the content will be passed
            content_id is id of instance of reading material , video or quiz that is made in the section.
        table : SectionContent
        while creating the instance:
                    section = id from url
                    content_type = will be made via constructor on initialization
                    content_id = models.PositiveIntegerField()
    """
    pass

class ActivateCourseView(APIView):
    """
        view to activate the course.
        trigger with POST request.
        in URL : course_id of selected instance.
        table : Course
        updating instance field:
                    change active from False to True
    """
    pass

class InActiveCourseView(APIView):
    """
        view to inactivate the course.
        trigger with POST request.
        in URL : course_id of selected instance.
        table : Course
        updating instance field:
                    change active from True to False        
    """
    pass

class EditCourseDetailsView(APIView):
    """
        view to edit the content of selected instance of course.
        should be made for inactive course usually.
        trigger with POST request.
        in URL : course_id of selected instance
        table : Course
        updating instance field:
                    title = request body
                    summary = request body
                    updated_at = now()
        and instance will be updated
    """
    pass

class ActiveCourseListView(generics.ListAPIView):
    """
        this API is used to retrive data from course table regarding all courses which are inactive.
        it is triggered with GET request.
    """
    pass

class SingleCourseDetailView(generics.DetailView):
    """
        view to be used to display the content of a selected course
        triggered with GET request.
        in URL : course_id of selected instance
        table : Course
        what will be displayed :
                    title
                    summary
                    updated_at
                    active
                    original_course.name # name of course whose updated version this course is
                    # related to number of version it is 
    """
    pass

class SingleCourseSectionsListView(APIView):
    """
        view used to display list of sections related to the selected course.
        trigger with GET request.
        in URL : course_id of selected instance
        table : Course
        what will happen :
                    list of sections related to the selected course will be displayed.
                    ordered by ascending number of section_number
    """
    pass

#can be used in editing phase
class SingleSectionDetailsView(APIView):
    """
        view used to display the content of selected section.
        trigger with GET request.
        in URL : course_id and section_id of selected instance
        table : Section
        what will be displayed :
                    title # only , when it is not there for editing
                    and name
    """
    pass



