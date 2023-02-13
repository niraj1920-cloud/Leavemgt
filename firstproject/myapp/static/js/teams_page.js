function showEmployees(team) {
    var team1 = document.getElementById("team1");
    var team2 = document.getElementById("team2");
    var team3 = document.getElementById("team3");
    var others = document.getElementById("others");
    team1.style.display = "none";
    team2.style.display = "none";
    team3.style.display = "none";
    others.style.display = "none";
    document.getElementById(team).style.display = "block";
}