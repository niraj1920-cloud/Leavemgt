const number=document.getElementById("phone").value;
  function validation(e)
  {
    if(e.value.length!=10)
    {
      document.getElementById("error1").innerHTML="number should be 10 digits"
    }
    else
    {
      document.getElementById("error1").innerHTML=""
    }

  }