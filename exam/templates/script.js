document.addEventListener("DOMContentLoaded", function() {
    const courseProgressContainer = document.getElementById("courseProgress");
  
    // Fetch course progress data from the backend API
    fetch('http://127.0.0.1:8000/lms/display-client-course-progress?user_id=YOUR_USER_ID')
      .then(response => response.json())
      .then(data => {
        // Loop through the retrieved data and create elements to display the course names and progress
        data.progress.forEach(course => {
          const courseDiv = document.createElement("div");
          courseDiv.classList.add("course");
          courseDiv.innerHTML = `
            <p>${course.course_name}: ${course.progress_percentage}% Progress</p>
          `;
          courseProgressContainer.appendChild(courseDiv);
        });
      })
      .catch(error => console.error('Error fetching course progress data:', error));
  });
  