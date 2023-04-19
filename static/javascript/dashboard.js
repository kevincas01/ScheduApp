

const completedInputs = document.querySelectorAll(".completedCheck");

// Loop through each input element
completedInputs.forEach((input) => {
    
  input.addEventListener("change", (event) => {
    
    const assignmentId = input.dataset.assignmentid;

    var xhr = new XMLHttpRequest();

    xhr.onreadystatechange = function() {
        if (this.readyState === 4 && this.status === 200) {
          var response = JSON.parse(this.responseText);
        
          if ('redirect' in response) {
            // Redirect the user to the specified URL
            console.log("redirecting")
            window.location.href = response.redirect;
        }
    }
    };
    
    xhr.open("POST", "/update_complete?assignmentId=" + assignmentId , true);
    xhr.send();

    // $('#confirmCheckModal').modal('show');
  });
});