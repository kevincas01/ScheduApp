const addButton = document.getElementById('add-task-input');

const inputList = document.getElementById('task_inputs');
let count = 0;

addButton.addEventListener('click', function() {
  // Create a new input element

  const newInput = document.createElement('input');
  newInput.type = 'text';
  newInput.className="form-control form-control-md"
  newInput.name = 'taskInput' + count;

  // Add the input element to the list
  inputList.appendChild(newInput);

  // Increment the count for the next input name
  count++;
});


// const assignment_course_input=document.getElementById('assignment_course_input');
// assignment_course_input.addEventListener('click',(event)=>{

//   // Get the courses that a user has
  
//   var xhr = new XMLHttpRequest();
//         xhr.onreadystatechange = function() {
//           if (this.readyState === 4 && this.status === 200) {
//             document.getElementById("assignments_modal_text").innerHTML = this.responseText;
//           }
//         };
        
        
//         xhr.open("GET", "/update_modal?year=" + year + "&month=" + month+ "&day=" + day, true);
//         xhr.send();

// });

// Display courses list
const courseNames=document.getElementById('course_name');
courseNames.addEventListener('click',(event) => {

  const courseList=document.getElementById('courses_list');

  var server = new XMLHttpRequest();
        server.onreadystatechange = function() {
          if (this.readyState === 4 && this.status === 200) {
            document.getElementById('courses_list').innerHTML = this.responseText
          }
        };
        
        server.open("GET", "get_course", true);
        server.send();

});

// Add a course to list
const courseAdd=document.getElementById('course_add_button');
courseAdd.addEventListener('click',(event) => {

  
  const course_name_input = document.getElementById('new_course_name_input').value;
  
  if (course_name_input==""){
    return
  }
  const course_name = document.getElementById('course_name');

  console.log(course_name.innerText)
  
  var server = new XMLHttpRequest();

  server.onreadystatechange = function() {
    if (this.readyState === 4 && this.status === 200) {
      console.log(course_name_input)
      course_name.innerText=course_name_input
      course_name_input.value=course_name_input

    }
  };
  
  server.open("POST", "add_course?courseName=" + course_name_input , true);
  server.send();

  

});

// CHOOSE A COURSE FROM LIST
const courseList=document.getElementById('courses_list');
courseList.addEventListener('click', (event)=>{
  
  if (event.target.tagName === 'H2') {
    console.log(event.target.textContent)
    document.getElementById('course_name').innerText = event.target.textContent; // Retrieves the text content of the clicked H2 element
    
    document.getElementById('course_name_input').value= event.target.textContent;
  }
});

var today=new Date().toJSON().slice(0, 10);

document.getElementById('assignment_date_input').value=today
document.getElementById('assignment_start_date_input').value=today


// ON SUBMIT FORM
const form = document.getElementById('assignment_form');
form.addEventListener('submit', (event) => {
  event.preventDefault(); // Prevents the default form submission behavior
  const assignment_name = document.getElementById('assignment_name_input').value;
  const assignment_date = document.getElementById('assignment_date_input').value;
  const assignment_time = document.getElementById('assignment_time_input').value;

  $('#assignment_modal').modal('hide');

  form.submit()

  const assignment_type=document.getElementById("assignment_type_input").value;

  const assignment_tasks=[]
  for(let i=5;i<form.elements.length-1;i++){
      assignment_tasks.push(form.elements[i].value)
      
  }

// Perform other actions here, Successfully addedh as making an AJAX request to submit the form data to a server
});

// Sort the assignments
const menuForm=document.getElementById("sort_menu")
menuForm.addEventListener('click',(event)=>{
  

  if (event.target.tagName === 'A') {
    var method=event.target.textContent
    console.log(method)
  }

  var server = new XMLHttpRequest();

  server.onreadystatechange = function() {
    if (this.readyState === 4 && this.status === 200) {
      document.getElementById('assignments_list').innerHTML = this.responseText
    }
  };
  
  server.open("GET", "/sort_assignments?method=" + method, true);
  server.send();

});

// Show assignments
$(document).on("click", "div[data-toggle='modal']", function() {

  var id = $(this).data('assignmentid');

  let url ="/showAssignment?id=" +encodeURIComponent(id)
    
    // if (request != null) request.abort() // ? confused about this

    var server = new XMLHttpRequest();
    server.onreadystatechange = function() {
      if (this.readyState === 4 && this.status === 200) {

        if (this.responseText!="False"){
          var response = JSON.parse(this.responseText);
        
          tasks_list.innerHTML=response.tasks;
          document.getElementById("intervals_list").innerHTML=response.intervals
          document.getElementById("assignment_modal_title").innerHTML=response.header

        }
        
      }
    };
    
    server.open("GET", url, true);
    server.send();


});

chooseTimes=document.getElementById("choose_times_button")
chooseTimes.addEventListener('click',(event)=>{

  startDate=document.getElementById('assignment_start_date_input').value
  endDate=document.getElementById('assignment_date_input').value


  let url ="/getUnavailableTimes?startDate=" +encodeURIComponent(startDate)+"&endDate="+encodeURIComponent(endDate)

  var server = new XMLHttpRequest();
    server.onreadystatechange = function() {
      if (this.readyState === 4 && this.status === 200) {

        document.getElementById('timesDiv').innerHTML=this.responseText
        
      }
    };
    
    server.open("GET", url, true);
    server.send();

})
