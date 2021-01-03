
$(document).ready(function() {
	$('#signup').submit(function(event) {
		event.preventDefault();

		var data = JSON.stringify({
			'email': $('input[name=email]').val(),
			'username': $('input[name=username]').val(),
			'password': $('input[name=password]').val()});

		$.ajax({
			headers: {
				'Accept': 'application/json',
				'Content-Type': 'application/json'},
			url: 'http://localhost:5000/users',
			type: 'POST',
			dataType: 'json',
			data: data
		}).done(function(response) {
			console.log(response)
			window.location.replace('/');
		});
	});

	$('#signin').submit(function(event) {
		event.preventDefault();

		var data = JSON.stringify({
			'email': $('input[name=email]').val(),
			'password': $('input[name=password]').val()});

		$.ajax({
			headers: {
				'Accept': 'application/json',
				'Content-Type': 'application/json'},
			url: 'http://localhost:5000/token',
			type: 'POST',
			dataType: 'json',
			data: data
		}).done(function(response) {
			console.log(response);
			window.location.replace('/');
		});
	});

	$('#delete').click(function(event) {
		event.preventDefault();

		var uuid = window.location.pathname.split('/');

		$.ajax({
			type: 'DELETE',
			url: 'http://localhost:5000/images/' + uuid[2],
			headers: {'Authorization': 'Bearer ' + access_token}
		}).done(function(response) {
			console.log(response);
			window.location.replace('/images');
		});
	});

	$(document).on('click', '#patch', function(event) {
		event.preventDefault();

		var uuid = window.location.pathname.split('/');

		var data = JSON.stringify({
			'name': document.getElementById('name').innerHTML,
			'description': document.getElementById('description').innerHTML,
			'private': document.getElementById('private').checked});

		$.ajax({
			headers: {
				'Accept': 'application/json',
				'Content-Type': 'application/json',
				'Authorization': 'Bearer ' + access_token},
			type: 'PATCH',
			url: 'http://localhost:5000/images/' + uuid[2],
			dataType: 'json',
			data: data
		}).done(function(response) {
			console.log(response);
			location.reload();
		});
	});


	$(document).on('click', '#edit', function(event) {
		event.preventDefault();

		$('#name').attr('contenteditable', 'true');
		$('#name').attr('style', 'background-color: #D0E8F2;');
		$('#description').attr('contenteditable', 'true');
		$('#description').attr('style', 'background-color: #D0E8F2;');

		var patchButton = $('#edit').clone();
		patchButton.attr('value', 'Save');
		patchButton.attr('id', 'patch');
		patchButton.appendTo('#buttons');

		document.getElementById('edit').remove();

		var cancelButton = $('#delete').clone();
		cancelButton.attr('value', 'Cancel');
		cancelButton.attr('id', 'cancel');
		cancelButton.appendTo('#buttons');

		$('<input id="private" type="checkbox" style="float: right; margin-left: 4px">').appendTo('#privatebutton');
		$('<label id="privatelabel" style="display: inline; float: right">Private</label>').appendTo('#privatebutton');

	});

	$(document).on('click', '#cancel', function() {
		$('#name').attr('contenteditable', 'false');
		$('#name').attr('style', 'background-color: #FFF;');
		$('#description').attr('contenteditable', 'false');
		$('#description').attr('style', 'background-color: #FFF;');

		document.getElementById('cancel').remove();

		var editButton = $('#patch').clone();
		editButton.attr('value', 'Edit');
		editButton.attr('id', 'edit');
		editButton.appendTo('#buttons');

		document.getElementById('patch').remove();
		document.getElementById('private').remove();
		document.getElementById('privatelabel').remove();
	});

	$(document).on('click', '#revoke', function() {
		$.ajax({
			url: 'http://localhost:5000/revoke',
			type: 'POST',
			headers: {'Authorization': 'Bearer ' + access_token}
		}).done(function(response) {
			console.log(response);
			window.location.replace('/');
		});
	});

	$('#upload').submit(function(event) {
		event.preventDefault();

		var formData = new FormData();
		
		formData.append('name', $('input[name=name]').val());
		formData.append('description', document.getElementById('description').value);
		formData.append('file', $('#file')[0].files[0]);
		formData.append('private', document.getElementById('private').checked);
		
		$.ajax({
			url: 'http://localhost:5000/images',
			type: 'POST',
			headers: {'Authorization': 'Bearer ' + access_token},
			data: formData,
			mimeType: 'multipart/form-data',
			enctype: 'multipart/form-data',
			contentType: false,
			processData: false
		}).done(function(response) {
			var json = $.parseJSON(response);
			console.log(json);
			window.location.replace('http://localhost:5000/images/' + json['uuid']);
		});
	});

	$(document).on('click', '#myimages', function() {
		$.ajax({
			url: 'http://localhost:5000/images',
			headers: {'Authorization': 'Bearer ' + access_token}
		}).done(function(response) {
			console.log(response);
			document.write(response);
		});
	});

	$(document).on('click', '#profile', function() {
		$.ajax({
			url: 'http://localhost:5000/user',
			headers: {'Authorization': 'Bearer ' + access_token}
		}).done(function(response) {
			console.log(response);
			document.write();
			document.write(response);
		});
	});
});
