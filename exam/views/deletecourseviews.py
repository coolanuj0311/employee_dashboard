from django.utils import timezone
from django.db.models import Q
from django.shortcuts import get_object_or_404, render
from rest_framework import status
from django.contrib import messages
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from exam.models.allmodels import (
    Course,
    UploadVideo,
    UploadReadingMaterial,
    CourseStructure,
    CourseRegisterRecord,
    CourseEnrollment,
    Progress,
    Quiz,
    Question,
    QuizAttemptHistory
)
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.decorators import method_decorator
# from exam.models.coremodels import *
from exam.serializers.createcourseserializers import (
    ActivateCourseSerializer,
    CourseSerializer, 
    CourseStructureSerializer,
    CreateChoiceSerializer,
    InActivateCourseSerializer, 
    UploadReadingMaterialSerializer, 
    UploadVideoSerializer, 
    QuizSerializer, 
    CreateCourseSerializer,
    CreateUploadReadingMaterialSerializer,
    CreateUploadVideoSerializer,
    CreateQuizSerializer,
    CreateQuestionSerializer,
)
import pandas as pd

class DeleteSelectedCourseView(APIView):
    """
        view to used for deleting a course instance
        triggers with POST/delete request.
        should be allowed for only [super admin].

        table : Course
        
        url : course_id

        for course.active == True -> not allowed (first convert it into inactive course)
        for course.active == False -> 
                delete instance of course whose id in url from course table
                delete instances related to it from courseregistrationrecords, coursestructure, courseenrollment, quizattempthistory - via foreign key relation (CASCADE delete)
                delete mapped instances of course_id in url with reading material , video material, quiz with whom it is in manytomany relation.
                        reading material , video material, quiz are in relation with this course only , then delete them from their tables too, similarly for questions in aspect of the quiz delete, and choicees will be deleted by cascade delete.
                
    """
    def post(self, request, course_id, format=None):
        try:
            # Fetch the course instance
            course = Course.objects.get(id=course_id)
            
            # Check if the course is active
            if course.active:
                return Response({"error": "Course must be inactive before deletion."}, status=status.HTTP_400_BAD_REQUEST)
            
            # Delete related instances if they are associated only with this course
            self.delete_related_instances(course)
            
            # Delete the course instance
            course.delete()
            
            return Response({"message": "Course deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        
        except Course.DoesNotExist:
            return Response({"error": "Course not found."}, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def delete_related_instances(self, course):
        # Delete mapped instances of course_id with reading material
        reading_materials = UploadReadingMaterial.objects.filter(courses=course)
        if reading_materials.count() == 1:
            reading_materials.delete()

        # Delete mapped instances of course_id with video material
        video_materials = UploadVideo.objects.filter(courses=course)
        if video_materials.count() == 1:
            video_materials.delete()

        # Delete mapped instances of course_id with quiz and associated questions
        quizzes = Quiz.objects.filter(courses=course)
        for quiz in quizzes:
            if quiz.questions.count() == 1:
                quiz.questions.all().delete()
                quiz.delete()
                
class DeleteSelectedReadingMaterialView(APIView):
    """
        view to used for deleting a course instance
        triggers with POST/delete request.
        should be allowed for only [super admin].

        table : UploadReadingMaterial
        
        url : course_id, reading_material_id

        for course.active == True -> not allowed (first convert it into inactive course)
        for course.active == False -> 
                check if readingmaterial whoes id is in url is in relation with courses other than this :
                        if yes -> then only delete the relation between the course and that material.
                        if no -> then delete the instance of reading material whoes id is in url
    """
    pass

class DeleteSelectedVideoMaterialView(APIView):
    """
        view to used for deleting a course instance
        triggers with POST/delete request.
        should be allowed for only [super admin].

        table : UploadVideo
        
        url : course_id, video_material_id

        for course.active == True -> not allowed (first convert it into inactive course)
        for course.active == False -> 
                check if video_material whose id is in url is in relation with courses other than this :
                        if yes -> then only delete the relation between the course and that material.
                        if no -> then delete the instance of video_material whose id is in url
    """
    pass

class DeleteSelectedQuizView(APIView):
    """
        view to used for deleting a course instance
        triggers with POST/delete request.
        should be allowed for only [super admin].

        table : Quiz
        
        url : course_id, quiz_id

        for course.active == True -> not allowed (first convert it into inactive course)
        for course.active == False -> 
                check if Quiz whose id is in url is in relation with courses other than this :
                        if yes -> then only delete the relation between the course and that Quiz.
                        if no -> then delete the instance of Quiz whose id is in url
    """
    pass

class DeleteSelectedQuestionView(APIView):
    """
        view to used for deleting a course instance
        triggers with POST/delete request.
        should be allowed for only [super admin].

        table : Question
        
        url : course_id, quiz_id , question_id

        for course.active == True -> not allowed (first convert it into inactive course)
        for course.active == False -> 
                check if Question whose id is in url is in relation with quizzes other than this :
                        if yes -> then only delete the relation between that question and  Quiz.
                        if no -> then delete the instance of Question whose id is in url
    """
    pass

class DeleteSelectedChoiceView(APIView):
    """
        view to used for deleting a course instance
        triggers with POST/delete request.
        should be allowed for only [super admin].

        table : Choice
        
        url : course_id, question_id , choice_id

        for course.active == True -> not allowed (first convert it into inactive course)
        for course.active == False -> 
                delete the selected choice instance from choice table
    """
    pass

# should allow multiple coursestructure instances to be deleted
class DeleteCourseStructureInstanceView(APIView):
    pass
