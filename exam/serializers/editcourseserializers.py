from rest_framework import serializers
from exam.models.allmodels import Choice, Course, CourseStructure, Notification, Question, UploadReadingMaterial, UploadVideo, Quiz

class EditCourseInstanceSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=100, required=True)
    summary = serializers.CharField(required=True)

    def validate(self, data):
        if not data['title'] or not data['summary']:
            raise serializers.ValidationError("Title and summary cannot be empty")
        return data
    
class NotificationSerializer(serializers.ModelSerializer):
    
    created_at = serializers.SerializerMethodField()
    
    def get_created_at(self, obj):
        return obj.created_at.strftime("%Y-%m-%d")
    
    def validate(self, data):
        # Field Existence and Null Field Handling
        required_fields = ['id', 'course', 'message', 'created_at']
        for field in required_fields:
            if field not in data or data[field] is None:
                raise serializers.ValidationError(f"{field} is required")
        return data
    
    class Meta:
        model = Notification
        fields = ['id', 'message', 'created_at']