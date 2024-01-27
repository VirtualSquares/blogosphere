function TextArea(){
   document.querySelector("ck-editor").style.visibility = "visible";
}

function ChangeColor(event){
  var text = document.getElementById("BlogArea").value;
  text.style.color = event.target.value;
}

