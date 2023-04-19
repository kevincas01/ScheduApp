
function validateArgs(str){
return str.includes('&') || str.includes('=');

}

const editButton=document.getElementById("edit_profile")
const saveButton=document.getElementById("save_profile")
const nameInput=document.getElementById("pref_name_input")
const minTimeInput=document.getElementById("min_time_input")
const dayStartInput=document.getElementById("day_start_input")
const dayEndInput=document.getElementById("day_end_input")

editButton.addEventListener('click',(event)=>{

editButton.style.display="None";
saveButton.style.display="Inline";
document.getElementById("profile_name").style.display="None";
nameInput.style.display="Inline";

document.getElementById("profile_min_time").style.display="None";
minTimeInput.style.display="Inline";

document.getElementById("profile_start_time").style.display="None";
dayStartInput.style.display="Inline";

document.getElementById("profile_end_time").style.display="None";
dayEndInput.style.display="Inline";

});

const alertPlaceholder = document.getElementById('alert')
    const appendAlert = (message) => {
    const wrapper = document.createElement('div')
    wrapper.innerHTML = [
        `<div class="alert alert-danger alert-dismissible" role="alert">`,
        `   <div>${message}</div>`,
        '   <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>',
        '</div>'
    ].join('')

    alertPlaceholder.append(wrapper)
    
    }
saveButton.addEventListener('click',(event)=>{

    if (validateArgs(nameInput.value)){
        console.log("alert")

        var myAlert = document.getElementById('name_alert');
        myAlert.style.display = 'block';

        setTimeout(function() {
        myAlert.style.display = 'none';
        }, 3000);

        return ;
    }


    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function() {
        if (this.readyState === 4 && this.status === 200) {
        console.log("EDITED")}

        

        editButton.style.display="Inline";
        saveButton.style.display="None";

        profileName=document.getElementById("profile_name")
        profileName.style.display="Inline";
        
        profileName.innerHTML=nameInput.value
        nameInput.style.display="None";
        
        minTime=document.getElementById("profile_min_time")
        minTime.style.display="Inline";
        minTime.innerHTML=minTimeInput.value+" minutes"

        minTimeInput.style.display="None";
        
        dayStart=document.getElementById("profile_start_time")
        dayStart.style.display="Inline";
        dayStart.innerHTML=dayStartInput.value;

        dayStartInput.style.display="None";
        
        dayEnd=document.getElementById("profile_end_time")
        dayEnd.style.display="Inline";
        dayEnd.innerHTML=dayEndInput.value
        dayEndInput.style.display="None";
        
    };


    xhr.open("POST", "/edit_profile?newName=" + nameInput.value + "&newMinTime=" + minTimeInput.value+ "&newDayStart=" + dayStartInput.value+ "&newDayEnd=" + dayEndInput.value, true);
    xhr.send();

});


