function addField(){
	// Container <div> where dynamic content will be placed
	var container = document.getElementById("container");

	// Row container with all the content
	var row = document.createElement("div");
	row.className = "row g-3 mb-1";
	container.appendChild(row);

	var start_datetime = document.createElement("div");
	var stop_datetime = document.createElement("div");
	start_datetime.className = "col";
	stop_datetime.className = "col";
	row.appendChild(start_datetime);
	row.appendChild(stop_datetime);

	var startInput = document.createElement("input");
	startInput.name = "start_datetime[]";
	startInput.type = "datetime-local";
	startInput.required = true;
	startInput.className = "form-control";
	start_datetime.appendChild(startInput);

	var stopInput = document.createElement("input");
	stopInput.name = "end_datetime[]";
	stopInput.type = "datetime-local";
	stopInput.required = true;
	stopInput.className = "form-control";
	stop_datetime.appendChild(stopInput);
}
