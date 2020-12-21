
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
			url: 'http://localhost:5000/images/' + uuid[1]
		}).done(function(response) {
			console.log(response);
			window.location.replace('/gallery');
		});
	});

	$(document).on('click', '#patch', function(event) {
		event.preventDefault();

		var uuid = window.location.pathname.split('/');

		var data = JSON.stringify({
			'name': document.getElementById('name').innerHTML,
			'description': document.getElementById('description').innerHTML});

		$.ajax({
			headers: {
				'Accept': 'application/json',
				'Content-Type': 'application/json'},
			type: 'PATCH',
			url: 'http://localhost:5000/images/' + uuid[1],
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
	});

	$('#upload').submit(function(event) {
		event.preventDefault();

		var formData = new FormData();
		
		formData.append('name', $('input[name=name]').val());
		formData.append('description', document.getElementById('description').value);
		formData.append('file', $('#file')[0].files[0]);
		
		$.ajax({
			url: 'http://localhost:5000/images',
			type: 'POST',
			data: formData,
			mimeType: 'multipart/form-data',
			enctype: 'multipart/form-data',
			contentType: false,
			processData: false
		}).done(function(response) {
			var json = $.parseJSON(response);
			console.log(json);
			window.location.replace('http://localhost:5000/' + json['uuid']);
		});
	});
});
