from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from django.core.exceptions import PermissionDenied
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.db import transaction
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, ValidationError
from django.utils import timezone
from exam.models.coremodels import *
from exam.serializers.registercourseserializers import *
from exam.models.allmodels import (
    Course,
    CourseRegisterRecord,
    CourseEnrollment,
)
from django.core.exceptions import ObjectDoesNotExist

'''
courseview.py----
AllCourseListDisplayView
ActiveCourseListDisplayView [Need to be used for registration Purpose]
'''

# =====================================================================
#      Views To CREATE Registration of Course with Customer instance(s)
# =====================================================================
class FirstVersionActiveCourseListView(APIView):
    """
        view to display [active] courses list from course table that have original_course = null and version_number = 1
        trigger with GET request
        should be allowed for only [super admin].
                
        table : Course
        
        what will be displayed:
                    id
                    title 
                    updated_at
                    version_number
    Response:
    [
        {
            "id": 1,
            "title": "Python Fundamentals",
            "updated_at": "2024-03-22",
            "version_number": 1
        },
        {
            "id": 2,
            "title": "Python Advanced",
            "updated_at": "2024-03-22",
            "version_number": 1
        }
    ]
    """
    '''
    courses will be filtered for which original_course = null and version_number = 1,
    list of such courses will be made and then displayed.
    '''
    def get(self, request):
        try:
            # Retrieve active courses with original_course null and version_number 1
            courses = Course.objects.filter(original_course__isnull=True, version_number=1, active=True).order_by('-updated_at')
            # Check if any courses are found
            if not courses:
                return Response({"error": "No active first version courses found."}, status=status.HTTP_404_NOT_FOUND)
            # Serialize the queryset
            serializer = FirstVersionActiveCourseListSerializer(courses, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ValidationError as ve:
            return Response({"error": "Validation Error: " + str(ve)}, status=status.HTTP_400_BAD_REQUEST)
        except Course.DoesNotExist:
            return Response({"error": "Course not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DerivedVersionActiveCourseListView(APIView):
    """
        view to display [active] courses list from course table that have original_course != null and active
        trigger with GET request
        should be allowed for only [super admin].
        
        in URL : course_id
            
        table : Course
        
        what will be displayed:
                    id
                    title 
                    updated_at
                    original_course.name
                    version_number
    Response:
    {
        "id": 1,
        "title": "Python Advanced",
        "updated_at": "2024-03-22",
        "original_course": "Python Fundamentals",
        "version_number": 2
    }
    """
    '''
        for course id in url , filter will be set on original_course and active is true
        list of filtered course will be made which have same original_course value(id) and then listed on the basis of version_number (ascending)
    '''
    def get(self, request, course_id):
        try:
            # Fetch the derived courses with the given original_course ID that are active
            derived_courses = Course.objects.filter(original_course=course_id, active=True).order_by('version_number','-updated_at')
            # Check if any courses are found
            if not derived_courses:
                return Response({"error": "No active derived courses found for the provided course ID."}, status=status.HTTP_404_NOT_FOUND)
            # Serialize the data
            serializer = DerivedVersionActiveCourseListSerializer(derived_courses, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ValidationError as ve:
            return Response({"error": "Validation Error: " + str(ve)}, status=status.HTTP_400_BAD_REQUEST)
        except Course.DoesNotExist:
            return Response({"error": "Course not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LMSCustomerListView(APIView):
    """
        view to display  list of customers who have resource privilege of LMS and are active
        trigger with GET request
        should be allowed for only [super admin].
        
        table : Customer_Resources, Resources , Customer 
        
        what will be displayed:
                    id
                    titles of customer
    """
    def get(self, request, format=None):
        try:
            # Retrieve customer IDs with LMS resource privilege
            customer_ids_with_lms = CustomerResources.objects.filter(resource__resource_name='LMS').values_list('customer_id', flat=True)
            # Check if any customers with LMS resource privilege are found
            if not customer_ids_with_lms:
                return Response({"error": "No customers found with LMS resource privilege."}, status=status.HTTP_404_NOT_FOUND)
            # Retrieve customers with active status
            customers = Customer.objects.filter(id__in=customer_ids_with_lms, is_active=True)
            # Check if any active customers are found
            if not customers:
                return Response({"error": "No active customers found with LMS resource privilege."}, status=status.HTTP_404_NOT_FOUND)
            # Serialize the queryset
            serializer = CustomerSerializer(customers, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ValidationError as ve:
            return Response({"error": "Validation Error: " + str(ve)}, status=status.HTTP_400_BAD_REQUEST)
        except CustomerResources.DoesNotExist:
            return Response({"error": "CustomerResources not found."}, status=status.HTTP_404_NOT_FOUND)
        except Customer.DoesNotExist:
            return Response({"error": "Customers not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CreateCourseRegisterRecordView(APIView):
    """
        view to create instances in CourseRegisterRecord.
        trigger with POST request
        should be allowed for only [super admin].
        
        table : CourseRegisterRecord
        
        in request body :
                        list of course_id =[..., ..., ..., ...]
                        list of customer_id =[..., ..., ..., ...]
        in response body :
                        each course in list will be mapped for all customers in list inside CourseRegisterRecord table
                        by default active will be true
                        
Request body :
        {
            "course_id": [1, 2, 3],
            "customer_id": [101, 102, 103]
        }
        
Response body :
        {
            "message": "Course register records created successfully."
            "record": [...]
        }
    """
    def post(self, request, *args, **kwargs):
        course_ids = request.data.get("course_id", [])
        customer_ids = request.data.get("customer_id", [])
        
        if not course_ids :
            return Response({"error": "Course IDs are missing"}, status=status.HTTP_400_BAD_REQUEST)
        if not customer_ids:
            return Response({"error": "Customer IDs are missing"}, status=status.HTTP_400_BAD_REQUEST)
        
        # List to hold created records and existing records
        created_records = []
        existing_records = []
        try:
            for course_id in course_ids:
                course = Course.objects.get(pk=course_id)
                for customer_id in customer_ids:
                    customer = Customer.objects.get(pk=customer_id)
                    # Check if record already exists
                    if CourseRegisterRecord.objects.filter(course=course_id, customer=customer_id, deleted_at__isnull=True ).exists():
                        record = CourseRegisterRecord.objects.get(course=course_id, customer=customer_id)
                        if record.active == False:
                            record.active = True
                            record_data = {
                                "id": record.id,
                                "customer": record.customer.id,
                                "course": record.course.id,
                                "created_at": record.created_at,
                                "active": record.active
                            }
                            existing_records.append(record_data)
                        else:
                            record_data = {
                                "id": record.id,
                                "customer": record.customer.id,
                                "course": record.course.id,
                                "created_at": record.created_at,
                                "active": record.active
                            }
                            existing_records.append(record_data)
                            continue  # Skip creation if the record already exists

                    record_data = {
                        'course': course.id,
                        'customer': customer.id,
                        'active': True
                    }
                    serializer = CourseRegisterRecordSerializer(data=record_data)
                    if serializer.is_valid():
                        record = serializer.save()
                        created_records.append(serializer.data)
                    else:
                        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            # Combine both lists into a single list
            all_records = created_records + existing_records
            return Response({
                "message": "Course register records created successfully.",
                "created_records": created_records,
                "existing_records": existing_records,
                "records":all_records
            }, status=status.HTTP_201_CREATED)
        except Course.DoesNotExist:
            return Response({"error": "One or more courses not found"}, status=status.HTTP_404_NOT_FOUND)
        except Customer.DoesNotExist:
            return Response({"error": "One or more customers not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# =====================================================================
#      View To DISPLAY Registration of Course with Customer records
# =====================================================================
class DisplayCourseRegisterRecordView(APIView):
    """
        view to display all instances of CourseRegisterRecord Table.
        trigger with GET request
        
        table : CourseRegisterRecord, Customer , Course
        
        what will be displayed:
                    id
                    customer.title,
                    course.title,
                    created_at,
                    active
    """
    def get(self, request, *args, **kwargs):
        try:
            # Retrieve all instances of CourseRegisterRecord from the database
            course_register_records = CourseRegisterRecord.objects.filter(deleted_at__isnull=True).order_by('-created_at')
            # Check if courses exist
            if not course_register_records:
                return Response({"message": "No customer-course register record found.", "data": []}, status=status.HTTP_404_NOT_FOUND)
            try:
                # Serialize the courses data
                serializer = DisplayCourseRegisterRecordSerializer(course_register_records, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except ValidationError as ve:
                return Response({"error": "Validation Error: " + str(ve)}, status=status.HTTP_400_BAD_REQUEST)
        except CourseRegisterRecord.DoesNotExist:
            return Response({"error": "CourseRegisterRecord not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# =====================================================================
#      View To DELETE Registration of Course with Customer instance(s)
# =====================================================================
# class DeleteCourseRegisterRecordView(APIView):
#     """
#     view to delete selected instance(s) of CourseRegisterRecord
    
#     table : CourseRegisterRecord
    
#     allowed to only super-admin.
    
#     in request body :
#                 records : list of CourseRegisterRecord instances will be passed.
#     selected instances will be deleted from the courseregistration record table , and hence along with this instance , all instances from course enrollment table , which users have same customer id as that in these records will be deleted too.
#     and record of all users in course enrollment table with same customer id will have there record deleted from quizattempthistory , take if there is any.
#     """
#     def post(self, request, format=None):
#         try:
#             record_ids = request.data.get("records", [])
#             if not record_ids:
#                 raise ValidationError("No record IDs provided.")
            
#             # Delete selected instances from CourseRegisterRecord table
#             deleted_records_count = CourseRegisterRecord.objects.filter(id__in=record_ids).delete()
            
#             # Check if any records were deleted
#             if deleted_records_count[0] > 0:
#                 customer_ids = CourseRegisterRecord.objects.filter(id__in=record_ids).values_list('customer_id', flat=True)

#                 # Delete related data from CourseEnrollment table if it exists
#                 try:
#                     CourseEnrollment.objects.filter(user__customer__in=customer_ids).delete()
#                 except ObjectDoesNotExist:
#                     pass  # Ignore if CourseEnrollment table doesn't exist
#                 # Delete related data from QuizAttemptHistory table if it exists
#                 try:
#                     QuizAttemptHistory.objects.filter(enrolled_user__customer__in=customer_ids).delete()
#                 except ObjectDoesNotExist:
#                     pass  # Ignore if QuizAttemptHistory table doesn't exist
                
#                 message = f"{deleted_records_count[0]} records deleted successfully."
#                 return Response({"message": message}, status=status.HTTP_200_OK)
#             else:
#                 return Response({"message": "No records deleted."}, status=status.HTTP_200_OK)
#         except ValidationError as ve:
#             return Response({"error": str(ve)}, status=status.HTTP_400_BAD_REQUEST)
#         except CourseRegisterRecord.DoesNotExist:
#             return Response({"error": "One or more records not found."}, status=status.HTTP_404_NOT_FOUND)
#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DeleteSingleCourseRegisterRecordInstanceView(APIView):
    """
    View to delete selected instance of CourseRegisterRecord.

    Table: CourseRegisterRecord

    Allowed to only super-admin.
    """
    def post(self, request, pk):
        try:
            # Get the record instance to delete
            registered_record = CourseRegisterRecord.objects.get(pk=pk)
            if not registered_record:
                raise NotFound(" Selected Record not found.")

            # Get customer ID associated with the record
            customer_id = registered_record.customer.id

            # Delete related data from CourseEnrollment table if it exists
            # CourseEnrollment.objects.filter(user__customer__id=customer_id).delete()
            enroll_records = CourseEnrollment.objects.filter(user__customer__id=customer_id)
            for record in enroll_records:
                record.active = False
                record.deleted_at = timezone.now()

            # Delete related data from QuizAttemptHistory table if it exists
            # QuizAttemptHistory.objects.filter(enrolled_user__customer__id=customer_id).delete()

            # Delete the record instance
            registered_record.active = False
            registered_record.deleted_at = timezone.now()
            return Response({"message": f"Record with ID {pk} deleted successfully."}, status=status.HTTP_200_OK)
        except CourseRegisterRecord.DoesNotExist:
            raise NotFound("Record not found.")
        except ObjectDoesNotExist:
            raise NotFound("Related records not found.")
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
# =================================================================
#      View To MANAGE/UPDATE Registration of Course with Customer
# =================================================================

# all the mapped records of course with company which are deactivated 
# should ensure that the customer could no longer see these courses to enroll their employees on them.

class DeactivateCourseRegistrationRecordView(APIView):
    """
    view to turn active status from True to False for selected instances of Course resgistration record.
    relations which are not active won't allow those courses to be appeared for those employeers to enroll their employees on it anymore, without affecting already studying ones.
    
    in request body : records list with id of selected instances.
    
    
    """
    def post(self, request, *args, **kwargs):
        record_ids = request.data.get("records", [])

        if not record_ids:
            return Response({"error": "Record IDs are missing"}, status=status.HTTP_400_BAD_REQUEST)

        # List to hold IDs of records that were successfully deactivated
        deactivated_records = []
        try:
            for record_id in record_ids:
                try:
                    record = CourseRegisterRecord.objects.get(pk=record_id)
                    if record.active and record.deleted_at is not None:
                        record.active = False
                        record.updated_at = timezone.now()
                        record.save()
                        deactivated_records.append(record_id)
                except CourseRegisterRecord.DoesNotExist:
                    return Response({"error": f"Record with ID {record_id} not found"}, status=status.HTTP_404_NOT_FOUND)
            # Check if any records were successfully deactivated
            if deactivated_records:
                return Response({"message": "Course registration records deactivated successfully.",
                                "deactivated_records": deactivated_records}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "No records deactivated."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ActivateCourseRegistrationRecordView(APIView):
    """
    view is to turn selected instances of courseregisterrecord table's active field to True if it is false.
    
    in request body : records list with id of selected instances.
    
    """
    def post(self, request, *args, **kwargs):
        record_ids = request.data.get("records", [])

        if not record_ids:
            return Response({"error": "Record IDs are missing"}, status=status.HTTP_400_BAD_REQUEST)

        activated_records = []
        try:
            for record_id in record_ids:
                try:
                    record = CourseRegisterRecord.objects.get(pk=record_id)
                    if not record.active and record.deleted_at is not None:
                        record.active = True
                        record.updated_at = timezone.now()
                        record.save()
                        activated_records.append(record_id)
                except CourseRegisterRecord.DoesNotExist:
                    return Response({"error": f"Record with ID {record_id} not found"}, status=status.HTTP_404_NOT_FOUND)

            if activated_records:
                return Response({"message": "Course registration records activated successfully.",
                                "activated_records": activated_records}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "No records activated."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class DisplayActiveCourseRegisterRecordView(APIView):
    """
        view to display active instances of CourseRegisterRecord Table.
        trigger with GET request
        
        table : CourseRegisterRecord, Customer , Course
        
        what will be displayed:
                    id
                    customer.title,
                    course.title,
                    created_at,
                    active
    """
    def get(self, request, *args, **kwargs):
        try:
            # Retrieve all instances of CourseRegisterRecord from the database
            course_register_records = CourseRegisterRecord.objects.filter(active=True, deleted_at__isnull=True).order_by('-created_at')
            # Check if courses exist
            if not course_register_records:
                return Response({"message": "No customer-course register record found.", "data": []}, status=status.HTTP_404_NOT_FOUND)
            try:
                # Serialize the courses data
                serializer = DisplayCourseRegisterRecordSerializer(course_register_records, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except ValidationError as ve:
                return Response({"error": "Validation Error: " + str(ve)}, status=status.HTTP_400_BAD_REQUEST)
        except CourseRegisterRecord.DoesNotExist:
            return Response({"error": "CourseRegisterRecord not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class DisplayInActiveCourseRegisterRecordView(APIView):
    """
        view to display inactive instances of CourseRegisterRecord Table.
        trigger with GET request
        
        table : CourseRegisterRecord, Customer , Course
        
        what will be displayed:
                    id
                    customer.title,
                    course.title,
                    created_at,
                    active
    """
    def get(self, request, *args, **kwargs):
        try:
            # Retrieve all instances of CourseRegisterRecord from the database
            course_register_records = CourseRegisterRecord.objects.filter(active=False ,deleted_at__isnull=True).order_by('-created_at')
            # Check if courses exist
            if not course_register_records:
                return Response({"message": "No customer-course register record found.", "data": []}, status=status.HTTP_404_NOT_FOUND)
            try:
                # Serialize the courses data
                serializer = DisplayCourseRegisterRecordSerializer(course_register_records, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except ValidationError as ve:
                return Response({"error": "Validation Error: " + str(ve)}, status=status.HTTP_400_BAD_REQUEST)
        except CourseRegisterRecord.DoesNotExist:
            return Response({"error": "CourseRegisterRecord not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)