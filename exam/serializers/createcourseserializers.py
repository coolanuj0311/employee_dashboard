from rest_framework import serializers
from exam.models.allmodels import Choice, Course, CourseStructure, Question, UploadReadingMaterial, UploadVideo, Quiz

class CreateCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['title', 'summary']
        
class CreateUploadReadingMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadReadingMaterial
        fields = ['title', 'reading_content']
        
class CreateUploadVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadVideo
        fields = ['title', 'video', 'summary']
        
class CreateQuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = ['title', 'random_order', 'answers_at_end', 'exam_paper', 'pass_mark']
        
class CreateQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['figure', 'content', 'explanation', 'choice_order']
        
class CreateChoiceSerializer(serializers.ModelSerializer):
    """
    Serializer for creating choices.
    """

    class Meta:
        model = Choice
        fields = ['choice', 'correct']

    def create(self, validated_data):
        question_id = self.context.get('question_id')
        question = Question.objects.get(pk=question_id)
        choice = Choice.objects.create(question=question, **validated_data)
        return choice
    
class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'

class CourseStructureSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseStructure
        fields = '__all__'

class UploadReadingMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadReadingMaterial
        fields = '__all__'

class UploadVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadVideo
        fields = '__all__'

class QuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = '__all__'

class InActivateCourseSerializer(serializers.Serializer):
    """
    Serializer for inactivating a course.
    """
    course_id = serializers.IntegerField()

    def validate_course_id(self, value):
        try:
            course = Course.objects.get(pk=value)
            return course
        except Course.DoesNotExist:
            raise serializers.ValidationError("Course does not exist.")
        
class ActivateCourseSerializer(serializers.Serializer):
    """
    Serializer for activating a course.
    """
    course_id = serializers.IntegerField()

    def validate_course_id(self, value):
        try:
            course = Course.objects.get(pk=value)
            # Check if there are any instances related to this course in CourseStructure
            if CourseStructure.objects.filter(course=course, content_type="quiz", content_id__isnull=False).exists():
                return course  # Return the course object instance
            else:
                raise serializers.ValidationError("Cannot activate course. Construct course structure first with minimum one quiz.")
        except Course.DoesNotExist:
            raise serializers.ValidationError("Course not found.")