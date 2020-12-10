
var token;

function signin() {
	var data = JSON.stringify({
		"email": document.getElementById("email").value,
		"password": document.getElementById("password").value
	});
	
	$.ajax(url='http://localhost:5000/token', settings={
		method: 'POST',
		data: data
	}).always(function() {
		alert(data);
	});
}

function signup() {
	var data = JSON.stringify({
		"username": document.getElementById("username").value,
		"password": document.getElementById("password").value,
		"email": document.getElementById("email").value
	});

	$.ajax(url='http://localhost:5000/users', settings={
		method: 'POST',
		data: data
	});
}

function upload() {
	var data = JSON.stringify({
		"name": document.getElementById("name").value,
		"description": document.getElementById("description").value,
		"filename": document.getElementById("file").value
	});

	$.ajax(url='http://localhost:5000/images', settings={
		method: 'POST',
		data: data,
		headers: {"Authorization": token}
	});
}
