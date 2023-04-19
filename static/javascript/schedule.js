
const months = ["January", "February", "March", "April", "May", "June", "July",
              "August", "September", "October", "November", "December"];

const monthsDict = {"January":1, "February":2, "March":3, "April":4, "May":5, "June":6,"July":7,
"August":8, "September":9, "October":10, "November":11, "December":12};

function changeMonth(delta) {
  // Get the current year and month from the HTML
  var currentYear = parseInt(document.getElementById("current_year").innerText);
  var currentMonth = document.getElementById("current_month").innerText;
  
  //Change the 
  currentMonth=monthsDict[currentMonth]
  
  // Calculate the new year and month
  var newMonth = currentMonth + delta;
  var newYear = currentYear;
  if (newMonth == 0) {
    newMonth = 12;
    newYear = currentYear - 1;
  } else if (newMonth == 13) {
    newMonth = 1;
    newYear = currentYear + 1;
  }
  const monthText=months[newMonth-1]

  // Update the month and year placeholders in the HTML
  document.getElementById("current_month").innerText = monthText;
  document.getElementById("current_year").innerText = newYear;

  if(document.getElementById("assignments_calendar").classList.contains("active")){
    var mode="assignments"
  }else{
    var mode="personal"
  }

  // Make an AJAX request to update the calendar with the new year and month
  var xhr = new XMLHttpRequest();
  xhr.onreadystatechange = function() {
    if (this.readyState === 4 && this.status === 200) {
      document.getElementById("cal").innerHTML = this.responseText;
    }
  };

  
  xhr.open("GET", "/update_calendar?year=" + newYear + "&month=" + newMonth+"&mode=" + mode, true);
  xhr.send();
}

$(document).on("click", "td[data-toggle='modal']", function() {
  // Code to open the modal and pass data
    
      // Extract the values of the data-* attributes
      var day = $(this).data('day');
      var month = $(this).data('month');
      var year = $(this).data('year');
    
      // Update the content of the modal with the corresponding values
      $('#modalDay').text(day);
      $('#modalMonth').text(months[month-1]);
      $('#modalYear').text(year);

      
      if(document.getElementById("assignments_calendar").classList.contains("active")){
        var mode="assignments"
      }else{
        var mode="personal"
      }

      var xhr = new XMLHttpRequest();
      xhr.onreadystatechange = function() {
        if (this.readyState === 4 && this.status === 200) {
          document.getElementById("assignments_modal_text").innerHTML = this.responseText;
        }
      };
      
      
      xhr.open("GET", "/update_modal?year=" + year + "&month=" + month+ "&day=" + day+"&mode="+mode, true);
      xhr.send();

  });


$(document).ready(function() {
  document.getElementById("assignments_calendar").classList.add("active")
});


document.getElementById("calendar_select").addEventListener("click",(event)=>{

    const calendar_mode=event.target.textContent

    if (calendar_mode=="Personal"){
      document.getElementById("personal_calendar").classList.add("active")
      document.getElementById("assignments_calendar").classList.remove("active")
      
    }
    else{
      document.getElementById("assignments_calendar").classList.add("active")
      document.getElementById("personal_calendar").classList.remove("active")
      
    }

  changeMonth(0)

});

var checkbox=document.getElementById("repeat_check")
var repeatForm=document.getElementById("repeat_form");
checkbox.addEventListener("change", function(event) {
  if (event.target.checked) {
    var containerDiv = document.createElement("div");
    containerDiv.style.display = "flex"; // Set display property to inline-block
    
    // Create input for number
    var numberInput = document.createElement("input");
    numberInput.type = "number";
    numberInput.className = "form-control ";
    numberInput.style.width="60px"
    numberInput.placeholder = 1;
    numberInput.value = "1";
    numberInput.name="repeatNum"
    
    
    // Create select for interval
    var selectInput = document.createElement("select");
    selectInput.className = "form-control";
    selectInput.style.width="80px"
    var intervalOptions = ["days", "weeks", "months", "years"];
    for (var i = 0; i < intervalOptions.length; i++) {
      var option = document.createElement("option");
      option.value = intervalOptions[i];
      option.text = intervalOptions[i];
      selectInput.add(option);
    }
    selectInput.name="repeatType"

    var dateInput = document.createElement("input");
    dateInput.type = "date";
    dateInput.className = "form-control";
    dateInput.placeholder = "1";
    
    
    dateInput.name="repeatUntilDate"
    
    // Append inputs to container div
    containerDiv.append('Repeats every:')
    containerDiv.appendChild(numberInput);
    containerDiv.appendChild(selectInput);
    
    // Append container div to repeat_form div
    repeatForm.appendChild(containerDiv);
    repeatForm.appendChild(dateInput);
    
    
    // Append inputs to repeat_form div
  } else {
    // If checkbox is unchecked, remove all child elements from repeat_form div
    while (repeatForm.firstChild) {
      repeatForm.firstChild.remove();
    }
  }
}); 