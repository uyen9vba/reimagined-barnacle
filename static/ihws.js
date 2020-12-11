
var token;

function signin() {
	var data = JSON.stringify({
		"email": document.getElementById("email").value,
		"password": document.getElementById("password").value
	});

	$.ajax(url='http://localhost:5000/token', settings={
		type: 'POST',
		data: data
	}).always(function(json) {
		alert(json);
		token = json[0];
	});
}

function signup() {
	var data = JSON.stringify({
		username: document.getElementById("username").value,
		password: document.getElementById("password").value,
		email: document.getElementById("email").value
	});

	alert(data);

	$.ajax({
		url: 'http://localhost:5000/users',
		type: 'POST',
		data: data
	});
}

function upload() {
	var data = JSON.stringify({
		"name": document.getElementById("name").value,
		"description": document.getElementById("description").value,
		"filename": document.getElementById('file').value.split(/(\\|\/)/g).pop()
	});

	alert(data);

	var id;

	$.ajax(url='http://localhost:5000/images', settings={
		type: 'POST',
		data: data,
		headers: {Authorization: token}
	}).always(function(json) {
		id = json['id'];
	});

	var formData = new FormData();
	formData.append('file', input.files[0]);

	$.ajax(url='http://localhost:5000/images/' + id + '/cover', settings={
		type: 'PUT',
		data: formData,
		contentType: 'multipart/form-data',
		mimeType: 'multipart/form-data',
		headers: {Authorization: token}
	});
}
