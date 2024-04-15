from rest_framework import serializers
from backend.models.allmodels import Course, CourseEnrollment
from backend.models.coremodels import User

class RegisteredCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'title']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name']
    
# class BulkEnrollmentSerializer(serializers.Serializer):
#     course_id = serializers.ListField(
#         child=serializers.IntegerField(),
#         min_length=1,
#         error_messages={'min_length': 'This list may not be empty.'}
#     )
#     user_id = serializers.ListField(
#         child=serializers.IntegerField(),
#         min_length=1,
#         error_messages={'min_length': 'This list may not be empty.'}
#     )

#     def validate_course_id(self, value):
#         # Additional validation for course_id can be added here
#         return value

#     def validate_user_id(self, value):
#         # Additional validation for user_id can be added here
#         return value
class CourseEnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseEnrollment
        fields = ['id', 'user', 'course', 'enrolled_at', 'active']

class CourseEnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseEnrollment
        fields = ['user', 'course', 'active']

    def create(self, validated_data):
        return CourseEnrollment.objects.create(**validated_data)     

class UnAssignCourseEnrollmentSerializer(serializers.Serializer):
    enrollment_ids = serializers.ListField(
        child=serializers.IntegerField(),  # Validates that each item in the list is an integer
        min_length=1,  # Ensures the list is not empty
        error_messages={
            'min_length': 'At least one enrollment ID must be provided.',  # Custom error message for empty list
        }
    )

class AssignCourseEnrollmentSerializer(serializers.Serializer):
    enrollment_ids = serializers.ListField(child=serializers.IntegerField())

