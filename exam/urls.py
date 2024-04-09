from django.contrib import admin
from django.urls import path

from .views.editcourseviews import EditCourseInstanceDetailsView, NotificationBasedOnCourseDisplayView
from .views.courseviews import (
    ActiveCourseListDisplayView,
    AllCourseListDisplayView,
    InActiveCourseListDisplayView,
    # RegisterCoursesOnCostumerListDisplayView,
    CourseInstanceDetailDisplayView,
    SingleCourseStructureListDisplayView,
    ReadingMaterialInstanceDisplayView,
    VideoInstanceDisplayView,
    QuizInstanceDisplayView,
    QuizTake,
    dummy_quiz_index,
    ReadingMaterialListPerCourseView,
    VideoMaterialListPerCourseView,
    QuizListPerCourseView,
    QuestionListPerQuizView
)
from .views.registercourseviews import (
    FirstVersionActiveCourseListView,
    DerivedVersionActiveCourseListView,
    LMSCustomerListView,
    CreateCourseRegisterRecordView,
    DisplayCourseRegisterRecordView,
    # DeleteCourseRegisterRecordView,
    DeleteSingleCourseRegisterRecordInstanceView,
    DeactivateCourseRegistrationRecordView,
    ActivateCourseRegistrationRecordView,
    DisplayActiveCourseRegisterRecordView,
    DisplayInActiveCourseRegisterRecordView
)
from .views.enrollcourseviews import (
    RegisteredCourseListView,
    UserListForEnrollment,
    CreateCourseEnrollmentView,
    DisplayCourseEnrollmentView,
    UnAssignCourseEnrollmentView,
    AssignCourseEnrollmentView
)
from .views.createcourseviews import (
    CreateCourseView,
    CreateReadingMaterialView,
    CreateVideoView,
    CreateQuizView,
    CreateCourseStructureForCourseView,
    CreateQuestionView,
    CreateChoiceView,
    ActivateCourseView,
    InActivateCourseView,
    CreateNewVersionCourseView
)
# from .views.editcourseviews import (
#     EditCourseInstanceDetailsView,
#     EditReadingMaterialView,
#     EditVideoMaterialView,
#     EditQuizDetailView,
#     EditExistingQuestionDetailsView,
#     EditQuestionChoicesView
# )
from django.urls import path
from .views.userdashboardviews import (
    CreateCourseCompletionStatusPerUserView,
    CreateQuizScoreView,
    EmployeeDashboard,
    UpdateCompleteQuizCountView,
    UpdateTotalScorePerCourseView,
    UpdateCourseCompletionStatusPerUserView,
    DisplayClientCourseProgressView,
    DisplayClientCourseCompletionStatusView,
    CountOfAssignedCoursesView, CountClientCompletedCourseView,

)




urlpatterns = [
    # path('courses/', CourseListView.as_view(), name='courses-list'),
    # path('customers/', CostumerListView.as_view(), name='customers-list'),
    # path('client-admin-courses/', ClientAdminCourseListView.as_view(), name='client-admin-courses-list'),
    # path('client-admin-employees/', ClientAdminEmployeeListView.as_view(), name='client-admin-employees-list'),
    # path('enrollments/', CourseEnrollmentDisplayView.as_view(), name='enrollments-list'),
    
    #courseview.py  views url
    path('courses/', AllCourseListDisplayView.as_view(), name='courses-list'),
    path('courses/active/', ActiveCourseListDisplayView.as_view(), name='active-courses-list'),
    path('courses/inactive/', InActiveCourseListDisplayView.as_view(), name='inactive-courses-list'),

    # path('courses/registered/', RegisterCoursesOnCostumerListDisplayView.as_view(), name='registered-courses-list'),
    # path('courses/unregistered/', UnRegisteredCoursesOnCostumerListDisplayView.as_view(), name='un-registered-courses-list'),
    # path('courses/enrolled/', EnrolledCoursesListDisplayView.as_view(), name='enrolled-courses-list'),
    path('course/<int:course_id>/', CourseInstanceDetailDisplayView.as_view(), name='course'),
    path('course-structure/<int:course_id>/', SingleCourseStructureListDisplayView.as_view(), name='course-structure'),
    path('course/<int:course_id>/reading/<int:content_id>/', ReadingMaterialInstanceDisplayView.as_view(), name='course-reading-material-instance'),
    path('course/<int:course_id>/video/<int:content_id>/', VideoInstanceDisplayView.as_view(), name='course-video-instance'),
    path('course/<int:course_id>/quiz/<int:content_id>/', QuizInstanceDisplayView.as_view(), name='course-quiz-instance'),
    path('course/<int:course_id>/readings/', ReadingMaterialListPerCourseView.as_view(), name='course-reading-material-list'),
    path('course/<int:course_id>/videos/', VideoMaterialListPerCourseView.as_view(), name='course-video-list'),
    path('course/<int:course_id>/quizzes/', QuizListPerCourseView.as_view(), name='course-quiz-list'),
    path('course/<int:course_id>/quiz/<int:quiz_id>/questions/', QuestionListPerQuizView.as_view(), name='quiz-question-list'),
    path('course/<int:course_id>/notifications/', NotificationBasedOnCourseDisplayView.as_view(), name='course_notifications'),



    
    path("<int:pk>/<slug:quiz_slug>/take/", QuizTake.as_view(), name="quiz_take"), #href="{% url 'quiz_take' pk=course.pk slug=quiz.slug %}
    #extra
    path('quiz/redirect/<int:course_id>/', view=dummy_quiz_index, name='quiz_index'),
    
    
    #registercourseviews.py views url
    path('courses/active/v1/', FirstVersionActiveCourseListView.as_view(), name='active-first-version-courses-list'),
    path('courses/derived-active/<int:course_id>/', DerivedVersionActiveCourseListView.as_view(), name='active-derived-version-course-list'),
    path('lms-customer/', LMSCustomerListView.as_view(), name='lms-customer-list'),
    path('create/course-register-record/', CreateCourseRegisterRecordView.as_view(), name='create-course-register-record'),
    path('display/course-register-record/', DisplayCourseRegisterRecordView.as_view(), name='course-register-record-list'),
    # path('delete/course-register-record/', DeleteCourseRegisterRecordView.as_view(), name='delete-course-register-record-list'),
    path('delete/course/<int:pk>/register-record/', DeleteSingleCourseRegisterRecordInstanceView.as_view(), name='delete-single-course-register-record'),
    path('deactivate/register-records/', DeactivateCourseRegistrationRecordView.as_view(), name='deactivate-register-records'),
    path('activate/register-records/', ActivateCourseRegistrationRecordView.as_view(), name='activate-register-records'),
    path('display/active/course-register-record/', DisplayActiveCourseRegisterRecordView.as_view(), name='active-course-register-record-list'),
    path('display/inactive/course-register-record/', DisplayInActiveCourseRegisterRecordView.as_view(), name='inactive-course-register-record-list'),

    
    
    #enrollcourseviews.py views url
    path('display/registered-course/', RegisteredCourseListView.as_view(), name='register-course-list'),
    path('display/users/', UserListForEnrollment.as_view(), name='users-list'),
    path('create/course-enrollments/', CreateCourseEnrollmentView.as_view(), name='create-course-enrollments-record'),
    path('display/course-enrollments/', DisplayCourseEnrollmentView.as_view(), name='course-enrollments-list'),
    path('enrollments/unassign/', UnAssignCourseEnrollmentView.as_view(), name='unassign-course-enrollment'),
    path('enrollments/assign/', AssignCourseEnrollmentView.as_view(), name='assign-course-enrollment'),
    
    #createcourseview.py views url
    path('create/course/v1/', CreateCourseView.as_view(), name='create-course-v1'),
    path('create/course/<int:course_id>/reading-material/', CreateReadingMaterialView.as_view(), name='create-course-reading-material'),
    path('create/course/<int:course_id>/video/', CreateVideoView.as_view(), name='create-course-video'),
    path('create/course/<int:course_id>/quiz/', CreateQuizView.as_view(), name='create-course-quiz'),
    path('create/course/<int:course_id>/course-structure/', CreateCourseStructureForCourseView.as_view(), name='create-course-structure'),
    path('create/<int:course_id>/quiz/<int:quiz_id>/question/', CreateQuestionView.as_view(), name='create-quiz-question'),
    path('create/question/<int:question_id>/choices/', CreateChoiceView.as_view(), name='create-question-choice'),
    path('active/course/<int:course_id>/', ActivateCourseView.as_view(), name='activate-course'),
    path('inactive/course/<int:course_id>/', InActivateCourseView.as_view(), name='inactivate-course'),
    path('create/course/<int:course_id>/versions/', CreateNewVersionCourseView.as_view(), name='create-course-v1'),

    
    #editcourseviews.py views url
    path('course/<int:course_id>/edit/', EditCourseInstanceDetailsView.as_view(), name='edit_course_instance'),
    path('create-course-completion-status/', CreateCourseCompletionStatusPerUserView.as_view(), name='create_course_completion_status'),
    path('create-quiz-score/', CreateQuizScoreView.as_view(), name='create_quiz_score'),
    path('update-complete-quiz-count/', UpdateCompleteQuizCountView.as_view(), name='update_complete_quiz_count'),
    path('update-total-score-per-course/', UpdateTotalScorePerCourseView.as_view(), name='update_total_score_per_course'),
    path('update-course-completion-status/', UpdateCourseCompletionStatusPerUserView.as_view(), name='update_course_completion_status'),
    path('display-client-course-progress/', DisplayClientCourseProgressView.as_view(), name='display_client_course_progress'),
    path('display-client-course-completion-status/', DisplayClientCourseCompletionStatusView.as_view(), name='display_client_course_completion_status'),
    
    path('count-assigned-courses/', CountOfAssignedCoursesView.as_view(), name='count_assigned_courses'),
    path('count-client-completed-courses/', CountClientCompletedCourseView.as_view(), name='count_client_completed_courses'),
    path('employee-dashboard/', EmployeeDashboard.as_view(), name='employee_dashboard'),




]
