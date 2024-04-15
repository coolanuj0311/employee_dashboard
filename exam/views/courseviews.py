from django.shortcuts import get_object_or_404, render
from rest_framework import status
from django.contrib import messages
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
# C:\Users\Anjali Sharma\Desktop\LMS\backend\custom_authentication\custom_mixins.py
# from backend.custom_authentication.custom_mixins import SuperAdminMixin
from exam.models.allmodels import (
    Course,
    CourseRegisterRecord,
    CourseEnrollment,
    Progress,
    Quiz,
    Question,
    QuizAttemptHistory,
    UploadReadingMaterial,
    UploadVideo
)
# from exam.serializers import (
#     CostumerDisplaySerializer,
#     CourseDisplaySerializer,
# )

from django.views.generic import (
    DetailView,
    ListView,
    TemplateView,
    FormView,
    CreateView,
    FormView,
    UpdateView,
)

from exam.forms import (
    QuestionForm,
)
from rest_framework.exceptions import NotFound, ValidationError
from django.core.exceptions import ObjectDoesNotExist


from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.decorators import method_decorator
from exam.models.coremodels import *
from exam.serializers.courseserializers import *

# TODO:
'''
course_list display for different type of users :
    god admin : when he see all courses , he should get all data except summary on the list of courses [course table]
    employer/client-admin : when he see list of courses in dashboard ; courses on which he is registered and their active status[courseregisterrecord]
                            for enrollment [courses for which registration is active [true]] [courseregisterrecord] [RegisterCoursesOnCostumerListDisplayView]
    employee : courses on which he is enrolled and are active themselves and if user is active for this enrollment too
'''
class AllCourseListDisplayView(APIView): #(SuperAdminMixin, APIView)
    
    """
        view to display all of the courses from course table irrespective of active status what is in courseversion table
        triggers with GET request
        should be allowed for only [super admin].
        
        table : Course, CourseVersion
        
        what will be displayed:
                    id
                    slug
                    title
                    created_at
                    updated_at
                    active
                    original_course 
                    version_number
    """
    def get(self, request, format=None):
        try:
            # Check permissions using the SuperAdminMixin
            '''
            if not self.has_super_admin_privileges(request):
                return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)
            '''
            # if not self.has_super_admin_privileges(request):
            #     user = request.user
            #     customer = Customer(id=user.customer.id)
            #     if not(Q(CourseRegisterRecord(customer=customer, active=True).exists())|Q(CourseEnrollment(user=user,active=True).exists())):
            #         return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)
            # Fetch all courses
            courses = Course.objects.filter(deleted_at__isnull=True)
            
            # Check if courses exist
            if not courses:
                raise NotFound("No courses found.")
            
            # Serialize the courses data
            serializer = CourseDisplaySerializer(courses, many=True)
            return Response({"data": serializer.data}, status=status.HTTP_200_OK)
        
        except (NotFound, ObjectDoesNotExist) as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)

        except ValidationError as e:
            return Response({"error": "Validation Error: " + str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ActiveCourseListDisplayView(APIView):
    """
        view to display [active] courses list from course table 
        trigger with GET request
        should be allowed for all.
        
        table : Course
        
        what will be displayed:
                    id
                    title 
                    updated_at
                    original_course [title to be extracted on frontend]
                    version_number
    """
    def get(self, request, format=None):
        try:
            # Fetch all courses
            courses = Course.objects.filter(active=True, deleted_at__isnull=True)
            # Check if courses exist
            if not courses:
                return Response({"message": "No active courses found.", "data": []}, status=status.HTTP_404_NOT_FOUND)
            try:
                # Serialize the courses data
                serializer = ActiveCourseDisplaySerializer(courses, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except ValidationError as ve:
                return Response({"error": "Validation Error: " + str(ve)}, status=status.HTTP_400_BAD_REQUEST)
        except Course.DoesNotExist:
            return Response({"error": "Course not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class InActiveCourseListDisplayView(APIView):
    """
        view to display [inactive] courses list from course table 
        trigger with GET request
        should be allowed for only [super admin].
        
        table : Course
        
        what will be displayed:
                    id
                    title 
                    updated_at
                    original_course [title to be extracted on frontend]
                    version_number
    """
    def get(self, request, format=None):
        try:
            # Fetch all courses
            courses = Course.objects.filter(active=False, deleted_at__isnull=True)
            # Check if courses exist
            if not courses:
                return Response({"message": "No inactive courses found.", "data": []}, status=status.HTTP_404_NOT_FOUND)
            try:
                # Serialize the courses data
                serializer = InActiveCourseDisplaySerializer(courses, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except ValidationError as ve:
                return Response({"error": "Validation Error: " + str(ve)}, status=status.HTTP_400_BAD_REQUEST)
        except Course.DoesNotExist:
            return Response({"error": "Course not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CourseInstanceDetailDisplayView(APIView):
    """
        view to display the instance of selected course.
        trigger with GET request.
        should be allowed for all users who have access to lms.
        
        in url : course_id
        
        table : Courses
        
        what will be displayed of selected course:
                    id
                    title,
                    summary,
                    updated_at,
                    original_course [title to be extracted on frontend],
                    version_number
        access : to all if authenticated
    """
    def get(self, request, course_id, *args, **kwargs):
        try:
            course = Course.objects.get(pk=course_id)
            if not course:
                return Response({"error": "No course found on provided course ID."}, status=status.HTTP_404_NOT_FOUND)
        except Course.DoesNotExist:
            return Response({"error": "Course not found"}, status=status.HTTP_404_NOT_FOUND)
        if not course.deleted_at :
            return Response({"error": "Deleted course is not allowded to be accessed"}, status=status.HTTP_403_FORBIDDEN )
        try:
            # Serialize the data
            serializer = CourseSerializer(course)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ValidationError as ve:
            return Response({"error": "Validation Error: " + str(ve)}, status=status.HTTP_400_BAD_REQUEST)
        except Course.DoesNotExist:
            return Response({"error": "Course not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SingleCourseStructureListDisplayView(APIView):
    """
        view will be used to display the list of instances of course structure table, whose course id is in url.
        trigger with GET request.
        should be allowed for all users who have access to lms.
        
        in URL : course_id
        
        table : CourseStructure
        
        what will be displayed:
                    id
                    order_number,
                    content_type,
                    content_id,
    """
    def get(self, request, course_id, format=None):
        try:
            course_structures = CourseStructure.objects.filter(course_id=course_id, active=True, deleted_at__isnull=True)
            if course_structures.exists():
                serializer = CourseStructureSerializer(course_structures, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({"error": "No course structures found for the specified course ID"}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as ve:
            return Response({"error": "Validation Error: " + str(ve)}, status=status.HTTP_400_BAD_REQUEST)
        except CourseStructure.DoesNotExist:
            return Response({"error": "Course Structure not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ReadingMaterialInstanceDisplayView(APIView):
    """
        view will be used to display the instance of reading material which is selected, of selected course.
        trigger with GET request.
        should be allowed to all users who have access to it and lms.
        
        in URL : course_id, content_id (passed through course structure that will be displayed first)
        
        table : UploadReadingMaterial
        
        what will be displayed:
                    id
                    title,
                    reading_content
    """
    def get(self, request, course_id,content_id, format=None):
        try:
            reading_material = UploadReadingMaterial.objects.get(
                courses__id=course_id, 
                id=content_id, 
                active=True, 
                deleted_at__isnull=True
                )
            if reading_material :
                serializer = ReadingMaterialSerializer(reading_material)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({"error": "No reading_material found for the specified ID"}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as ve:
            return Response({"error": "Validation Error: " + str(ve)}, status=status.HTTP_400_BAD_REQUEST)
        except UploadReadingMaterial.DoesNotExist:
            return Response({"error": "Reading material instance not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class VideoInstanceDisplayView(APIView):
    """
        view will be used to display the instance of video which is selected, of selected course.
        trigger with GET request.
        should be allowed to all users who have access to it and lms.
        
        in URL : course_id, content_id (passed through course structure that will be displayed first)
        
        table : UploadVideo
        
        what will be displayed:
                    id
                    title,
                    video,
                    summary
    """
    def get(self, request, course_id,content_id, format=None):
        try:
            video_material = UploadVideo.objects.get(
                courses__id=course_id, 
                id=content_id, 
                active=True, 
                deleted_at__isnull=True
                )
            if video_material:
                serializer = VideoMaterialSerializer(video_material)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({"error": "No video_material found for the specified ID"}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as ve:
            return Response({"error": "Validation Error: " + str(ve)}, status=status.HTTP_400_BAD_REQUEST)
        except UploadVideo.DoesNotExist:
            return Response({"error": "Video instance not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class QuizInstanceDisplayView(APIView):
    """
        view will be used to display the instance of quiz which is selected if they are active , of selected course.
        trigger with GET request.
        should be allowed to all users who have access to it and lms.
        
        in URL : course_id, content_id (passed through course structure that will be displayed first)
        
        table : Quiz
        
        what will be displayed:
                    id
                    title,
                    description
    """
    def get(self, request, course_id,content_id, format=None):
        try:
            quiz = Quiz.objects.get(
                courses__id=course_id, 
                id=content_id, 
                active=True, 
                deleted_at__isnull=True
                )
            if quiz:
                serializer = QuizSerializer(quiz)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({"error": "No quiz found for the specified ID"}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as ve:
            return Response({"error": "Validation Error: " + str(ve)}, status=status.HTTP_400_BAD_REQUEST)
        except UploadVideo.DoesNotExist:
            return Response({"error": "Quiz instance not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# now sitting function will come that will start the quiz and display it's related questions and choices, and update quiz attempt history table for the user in request.

# @method_decorator([login_required], name="dispatch")
class QuizTake(FormView):
    form_class = QuestionForm
    template_name = "question.html"
    result_template_name = "result.html"
    # single_complete_template_name = 'single_complete.html'

    def dispatch(self, request, *args, **kwargs):
        self.quiz = get_object_or_404(Quiz, slug=self.kwargs["quiz_slug"])
        self.course = get_object_or_404(Course, pk=self.kwargs["pk"])
        # quizQuestions = Question.objects.filter(quiz=self.quiz).count()
        quiz_questions_count = self.quiz.questions.count()
        course = get_object_or_404(Course, pk=self.kwargs["pk"])

        if quiz_questions_count <= 0:
            messages.warning(request, f"Question set of the quiz is empty. try later!")
            return redirect("quiz_index", self.course.id) # redirecting to previous page as this quiz can't be started.

        # =================================================================
        user_header = request.headers.get("user")
        enrolled_user = get_object_or_404(User, pk=13)
        # ===============================
        self.sitting = QuizAttemptHistory.objects.user_sitting(
            enrolled_user,
            # request.user, 
            self.quiz, 
            self.course
        )

        if self.sitting is False:
            # return render(request, self.single_complete_template_name)
            messages.info(
                request,
                f"You have already sat this exam and only one sitting is permitted",
            )
            return redirect("quiz_index", self.course.id)

        return super(QuizTake, self).dispatch(request, *args, **kwargs)

    def get_form(self, *args, **kwargs):
        self.question = self.sitting.get_first_question()
        self.progress = self.sitting.progress()
        form_class = self.form_class

        return form_class(**self.get_form_kwargs())

    def get_form_kwargs(self):
        kwargs = super(QuizTake, self).get_form_kwargs()

        return dict(kwargs, question=self.question)

    def form_valid(self, form):
        self.form_valid_user(form)
        if self.sitting.get_first_question() is False:
            self.sitting.mark_quiz_complete()
            return self.final_result_user()

        self.request.POST = {}

        return super(QuizTake, self).get(self, self.request)

    def get_context_data(self, **kwargs):
        context = super(QuizTake, self).get_context_data(**kwargs)
        context["question"] = self.question
        context["quiz"] = self.quiz
        context["course"] = get_object_or_404(Course, pk=self.kwargs["pk"])
        if hasattr(self, "previous"):
            context["previous"] = self.previous
        if hasattr(self, "progress"):
            context["progress"] = self.progress
        return context

    def form_valid_user(self, form):
        # =================================================================
        user_header = self.request.headers.get("user")
        enrolled_user = get_object_or_404(User, pk=13)
        # ===============================
        # progress, _ = Progress.objects.get_or_create(user=self.request.user)
        progress, _ = Progress.objects.get_or_create(enrolled_user=enrolled_user)
        guess = form.cleaned_data["answers"]
        is_correct = self.question.check_if_correct(guess)

        if is_correct is True:
            self.sitting.add_to_score(1)
            progress.update_score(self.question, 1, 1)
        else:
            self.sitting.add_incorrect_question(self.question)
            progress.update_score(self.question, 0, 1)

        if self.quiz.answers_at_end is not True:
            self.previous = {
                "previous_answer": guess,
                "previous_outcome": is_correct,
                "previous_question": self.question,
                "answers": self.question.get_choices(),
                "question_type": {self.question.__class__.__name__: True},
            }
        else:
            self.previous = {}

        self.sitting.add_user_answer(self.question, guess)
        self.sitting.remove_first_question()

    def final_result_user(self):
        results = {
            "course": get_object_or_404(Course, pk=self.kwargs["pk"]),
            "quiz": self.quiz,
            "score": self.sitting.get_current_score,
            "max_score": self.sitting.get_max_score,
            "percent": self.sitting.get_percent_correct,
            "sitting": self.sitting,
            "previous": self.previous,
            "course": get_object_or_404(Course, pk=self.kwargs["pk"]),
        }

        self.sitting.mark_quiz_complete()

        if self.quiz.answers_at_end:
            results["questions"] = self.sitting.get_questions(with_answers=True)
            results["incorrect_questions"] = self.sitting.get_incorrect_questions

        if (
            self.quiz.exam_paper is False
            # or self.request.user.is_superuser
            # or self.request.user.is_lecturer
        ):
            self.sitting.delete()

        return render(self.request, self.result_template_name, results)

def dummy_quiz_index(request, course_id):
    # Retrieve the course object
    course = Course.objects.get(pk=course_id)
    
    # Render the quiz index template with the course ID in the context
    return render(request, 'quiz_index.html', {'course_id': course_id, 'course': course})

# #################################
class ReadingMaterialListPerCourseView(APIView):
    """
    view to display the list of active reading material
    GET request
    
    hould be allowed for only [super admin].
    
    in url : course_id
    what will be displayed :
            title
            uploaded_at
    """
    def get(self, request, course_id, format=None):
        try:
            reading_materials = UploadReadingMaterial.objects.filter(
                courses__id=course_id, 
                active=True, 
                deleted_at__isnull=True
            )
            serializer = ReadingMaterialListPerCourseSerializer(reading_materials, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ValidationError as ve:
            return Response({"error": "Validation Error: " + str(ve)}, status=status.HTTP_400_BAD_REQUEST)
        except UploadReadingMaterial.DoesNotExist:
            return Response({"error": "No reading materials found for the specified course ID"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class VideoMaterialListPerCourseView(APIView):
    """
    view to display the list of active video material
    GET request
    in url : course_id
    
    hould be allowed for only [super admin].
    
    what will be displayed :
            title
            uploaded_at
    """
    def get(self, request, course_id, format=None):
        try:
            video_materials = UploadVideo.objects.filter(
                courses__id=course_id, 
                active=True, 
                deleted_at__isnull=True
            )
            serializer = VideoMaterialListPerCourseSerializer(video_materials, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ValidationError as ve:
            return Response({"error": "Validation Error: " + str(ve)}, status=status.HTTP_400_BAD_REQUEST)
        except UploadReadingMaterial.DoesNotExist:
            return Response({"error": "No video materials found for the specified course ID"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class QuizListPerCourseView(APIView):
    """
    view to display the list of active quiz
    GET request
    
    hould be allowed for only [super admin].
    
    in url : course_id
    what will be displayed :
            title
            created_at
    """
    def get(self, request, course_id, format=None):
        try:
            quizzes = Quiz.objects.filter(
                courses__id=course_id, 
                active=True, 
                deleted_at__isnull=True
            )
            serializer = QuizListPerCourseSerializer(quizzes, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ValidationError as ve:
            return Response({"error": "Validation Error: " + str(ve)}, status=status.HTTP_400_BAD_REQUEST)
        except UploadReadingMaterial.DoesNotExist:
            return Response({"error": "No quiz found for the specified course ID"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class QuestionListPerQuizView(APIView):
    """
    view to display the list of active questions
    GET request
    
    hould be allowed for only [super admin].
    
    in url : course_id, quiz_id
    what will be displayed :
            content
            created_at
    """
    def get(self, request, course_id,quiz_id, format=None):
        try:
            questions = Question.objects.filter(
                quizzes__id=quiz_id, 
                active=True, 
                deleted_at__isnull=True
            )
            serializer = QuestionListPerQuizSerializer(questions, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ValidationError as ve:
            return Response({"error": "Validation Error: " + str(ve)}, status=status.HTTP_400_BAD_REQUEST)
        except UploadReadingMaterial.DoesNotExist:
            return Response({"error": "No question found for the specified quiz ID"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)