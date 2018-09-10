	var canvasWidth = 1000;
	var canvasHeight = 450;
	var curColor = "#000000";
	var radius = 3;
	var xFreehand = new Array();
	var yFreehand = new Array();
	var dragFreehand = new Array();
	var xLine = new Array();
	var yLine = new Array();
	var xBox = new Array();
	var yBox = new Array();
	var xMousePos = null;
	var yMousePos = null;
	var mouseDown;
	var canvas;
	var canvasContext;

	// adapted from http://www.williammalone.com/articles/create-html5-canvas-javascript-drawing-app/js/javascript.js; Apache 2.0 Licensed

	function getDrawMode() {
		const modeInfo = JSON.parse(document.getElementById('drawMode_info').innerHTML);
		return modeInfo.choices[modeInfo.i]
	}

	function getGraphType() {
		return document.getElementById('graphTypeIndicator').innerHTML;
	}

	function drawingIsAllowed() {
		return document.getElementById('showDataIndicator').innerHTML === "false";
	}

	function getX(clickEvent, offsetLeft) {
		return clickEvent.pageX - offsetLeft;
	}

	function getY(clickEvent, offsetTop) {
		return clickEvent.pageY - offsetTop;
	}

	function isOdd(n) {
		return Math.abs(n % 2) === 1;
	}

	function prepareCanvas() {

		canvas = document.createElement('canvas');
		canvas.setAttribute('id', 'canvasSimple');
		canvas.setAttribute('width', canvasWidth);
		canvas.setAttribute('height', canvasHeight);
		canvas.setAttribute('style', "position:absolute")
		$('#graph_container_container').prepend(canvas);

		if(typeof G_vmlCanvasManager != 'undefined') {
			canvas = G_vmlCanvasManager.initElement(canvas);
		}

		canvasContext = canvas.getContext("2d");

		const isWithinPlotBorder = (e) => {
			try {
				const panes = document.getElementById("graph").querySelectorAll(".nsewdrag");
				for (let i=0; i<panes.length; i++) {
					const borderRect = panes[i].getBoundingClientRect();
					if (e.clientX >= borderRect.x && e.clientX <= borderRect.x+borderRect.width
					&& e.clientY >= borderRect.y && e.clientY <= borderRect.y+borderRect.height) {
						return true;
					}
				}
				return false;
			} catch (err) {
				return false;
			}
		};

		$('#graph_container_container').mousedown(function(e) {
			mouseDown = true;
			if(drawingIsAllowed() && isWithinPlotBorder(e)) {
				const drawMode = getDrawMode();
				if (drawMode === 'Freehand') {
					xFreehand.push(getX(e, this.offsetLeft));
					yFreehand.push(getY(e, this.offsetTop));
					dragFreehand.push(false);
				}
				else if (drawMode === 'Line') {
					xLine.push(getX(e, this.offsetLeft));
					yLine.push(getY(e, this.offsetTop));
				}
				else if (drawMode === 'Box') {
					xBox.push(getX(e, this.offsetLeft));
					yBox.push(getY(e, this.offsetTop));
				}
				redrawCanvas();
			}
		});

		$(document).mouseup(function(e) {
			// if (drawingIsAllowed() && isWithinPlotBorder(e)) {
			// 	const graphType = getGraphType();
			// 	const drawMode = getDrawMode();
			// 	if (graphType === "Box Plot" && drawMode === "Box" && xBox.length > 0 && (xBox.length%2) === 0) {
			// 		const drawModeInfo = document.getElementById('drawMode_info');
			// 		drawModeInfo.innerHTML = JSON.stringify({choices: ['Freehand', 'Line', 'Box'], i: 1});
			// 		// document.getElementById("drawingControl_slider_container").querySelector(".rc-slider-mark").children[2].innerHTML = "Draw: Line";
			// 	} else if (graphType === "Dot Plot" && drawMode === "Line" && xLine.length > 0 && (xLine.length%2) === 0) {
			// 		const drawModeInfo = document.getElementById('drawMode_info');
			// 		drawModeInfo.innerHTML = JSON.stringify({choices: ['Freehand', 'Line', 'Box'], i: 0});
			// 		// document.getElementById("drawingControl_slider_container").querySelector(".rc-slider-mark").children[2].innerHTML = "Draw: Freehand";
			// 	}
			// }
			// const clear = () => {
			if (document.getElementById("graphtypeslider_container").contains(e.target) && (e.target.className === "rc-slider-handle" ||
			e.target.classList.contains("rc-slider-mark-text") || e.target.classList.contains("rc-slider-dot"))) {
			// if (document.getElementById('clear_drawing').innerHTML === "true" ||
			// (e.target.className === "rc-slider-handle" && e.target.style.bottom === "50%") ||
			// (e.target.classList.contains("rc-slider-mark-text") && e.target.innerHTML === "Reset")) {
				document.getElementById("drawingInstructions").style.display = "block";
				xFreehand = new Array();
				yFreehand = new Array();
				dragFreehand = new Array();
				xLine = new Array();
				yLine = new Array();
				xBox = new Array();
				yBox = new Array();
				redrawCanvas();
				// document.getElementById('clear_drawing').innerHTML = "false";
				const graphType = getGraphType();
				const drawModeInfo = document.getElementById('drawMode_info');
				// const drawModeDisplay = document.getElementById("drawingControl_slider_container").querySelector(".rc-slider-mark").children[2];
				const drawModeChoices = ['Freehand', 'Line', 'Box'];
				if (graphType==="Density Plot"||graphType==="Violin Plot"||graphType==="Table") {
					drawModeInfo.innerHTML = JSON.stringify({choices: drawModeChoices, i: 0});
					// drawModeDisplay.innerHTML = "Draw: Freehand";
				} else if (graphType === "Dot Plot") {
					drawModeInfo.innerHTML = JSON.stringify({choices: drawModeChoices, i: 1});
					// drawModeDisplay.innerHTML = "Draw: Line";
				} else {
					drawModeInfo.innerHTML = JSON.stringify({choices: drawModeChoices, i: 2});
					// drawModeDisplay.innerHTML = "Draw: Box";
				}
			}
			// };
			// const timeout = 100;
			// setTimeout(() => {
			// 	clear();
			// 	setTimeout(() => {
			// 		clear();
			// 		setTimeout(() => {
			// 			clear();
			// 			setTimeout(() => {
			// 				clear();
			// 				setTimeout(() => {
			// 					clear();
			// 				}, timeout);
			// 			}, timeout);
			// 		}, timeout);
			// 	}, timeout);
			// }, timeout);
			// if (document.getElementById("drawingControl_slider_container").contains(e.target) && ((e.target.className === "rc-slider-handle" && e.target.style.bottom === "100%") ||
			// (e.target.classList.contains("rc-slider-mark-text") && e.target.innerHTML.length >= 6 && e.target.innerHTML.substring(0,6) === "Draw: "))) {
			// 	if (drawingIsAllowed()) {
			// 		const drawModeInfo = document.getElementById('drawMode_info');
			// 		drawModeInfo.innerHTML = JSON.stringify({choices: ['Freehand', 'Line', 'Box'], i: (JSON.parse(drawModeInfo.innerHTML).i+1)%3});
			// 		const sliderLabel = e.target.classList.contains("rc-slider-mark-text")? e.target:e.target.nextElementSibling.children[2];
			// 		sliderLabel.innerHTML = "Draw: " + getDrawMode();
			// 	}
			// }
			const tuningSliderContainer = document.getElementById("graphTuning_slider_container")
			const graphType = getGraphType();
			if (graphType === "Box Plot" && tuningSliderContainer && tuningSliderContainer.contains(e.target)) {
				let clickedString = false;
				if (e.target.classList.contains("rc-slider-mark-text")) {
					clickedString = e.target.innerHTML;
				} else if (e.target.classList.contains("rc-slider-dot")) {
					let index = 0;
					let currentElement = e.target;
					while (currentElement.previousElementSibling) {
						index++;
						currentElement = currentElement.previousElementSibling;
					}
					clickedString = tuningSliderContainer.querySelector(".rc-slider").querySelector(".rc-slider-mark").children[index].innerHTML;
				} else if (e.target.classList.contains("rc-slider-handle")) {
					clickedString = tuningSliderContainer.querySelector(".rc-slider").querySelector(".rc-slider-mark").children[parseInt(e.target.getAttribute("aria-valuenow"), 10)].innerHTML;
				}
				if (clickedString) {
					document.getElementById("boxPlotToggles-" + clickedString).dispatchEvent(new MouseEvent('click', {bubbles: true, cancelable: true, view: window}));
				}
			}
		});

		$('#graph_container_container').mousemove(function(e) {
			xMousePos = getX(e, this.offsetLeft);
			yMousePos = getY(e, this.offsetTop);
			if(drawingIsAllowed() && isWithinPlotBorder(e)) {
				const drawMode = getDrawMode();
				if (drawMode === 'Freehand') {
					if(mouseDown) {
						xFreehand.push(getX(e, this.offsetLeft));
						yFreehand.push(getY(e, this.offsetTop));
						dragFreehand.push(true);
						redrawCanvas();
					}
				}
				if (drawMode === 'Line') {
					if (isOdd(xLine.length)) {
						redrawCanvas();
					}
				}
				else if (isOdd(xLine.length)) {
					xLine.pop();
					yLine.pop();
					redrawCanvas();
				}
				if (drawMode === 'Box') {
					if (isOdd(xBox.length)) {
						redrawCanvas();
					}
				}
				else if (isOdd(xBox.length)) {
					xBox.pop();
					yBox.pop();
					redrawCanvas();
				}
			}
		});

		$('#graph_container_container').mouseup(function(e) {
			mouseDown = false;
		});

		$('#graph_container_container').mouseleave(function(e) {
			mouseDown = false;
		});

		$(document).dblclick(function(e) {
			if (isWithinPlotBorder(e)) {
				document.getElementById("showDataButton").dispatchEvent(new MouseEvent('click', {bubbles: true, cancelable: true, view: window}));
			}
		});
		
		$(document).keyup(function(e) {
			if (getDrawMode() === 'Line' && isOdd(xLine.length)) {
				xLine.pop();
				yLine.pop();
				redrawCanvas();
			}
			if (getDrawMode() === 'Box' && isOdd(xBox.length)) {
				xBox.pop();
				yBox.pop();
				redrawCanvas();
			}
		});

	}

	function redrawCanvas() {

		if (xFreehand.length+xLine.length+xBox.length > 0) {
			document.getElementById("drawingInstructions").style.display = "none";
		}

		canvasContext.clearRect(0, 0, canvasWidth, canvasHeight);
		canvasContext.strokeStyle = curColor;
		canvasContext.lineJoin = "round";
		canvasContext.lineWidth = radius;
		  
		for(var i=0; i < xFreehand.length; i++) {   
			canvasContext.beginPath();
			if (dragFreehand[i] && i) {
				canvasContext.moveTo(xFreehand[i-1], yFreehand[i-1]);
			} else {
				canvasContext.moveTo(xFreehand[i]-1, yFreehand[i]);
			}
			canvasContext.lineTo(xFreehand[i], yFreehand[i]);
			canvasContext.closePath();
			canvasContext.stroke();
		}

		for(var i=1; i<xLine.length; i+=2) {
			canvasContext.beginPath();
			canvasContext.moveTo(xLine[i-1], yLine[i-1]);
			canvasContext.lineTo(xLine[i], yLine[i]);
			canvasContext.closePath();
			canvasContext.stroke();
		}

		for(var i=1; i<xBox.length; i+=2) {
			var width = Math.abs(xBox[i] - xBox[i-1]);
			var minX = Math.min(xBox[i], xBox[i-1]);
			var height = Math.abs(yBox[i] - yBox[i-1])
			var minY = Math.min(yBox[i], yBox[i-1]);
			canvasContext.beginPath();
			canvasContext.rect(minX, minY, width, height);
			canvasContext.closePath();
			canvasContext.stroke();
		}

		const drawMode = getDrawMode();
		if (drawMode === 'Line' && isOdd(xLine.length) && xMousePos !== null) {
			canvasContext.beginPath();
			canvasContext.moveTo(xLine[xLine.length-1], yLine[yLine.length-1]);
			canvasContext.lineTo(xMousePos, yMousePos);
			canvasContext.closePath();
			canvasContext.stroke();
		}
		else if (drawMode === 'Box' && isOdd(xBox.length) && xMousePos !== null) {
			var width = Math.abs(xMousePos - xBox[xBox.length-1]);
			var minX = Math.min(xMousePos, xBox[xBox.length-1]);
			var height = Math.abs(yMousePos - yBox[yBox.length-1]);
			var minY = Math.min(yMousePos, yBox[yBox.length-1]);
			canvasContext.beginPath();
			canvasContext.rect(minX, minY, width, height);
			canvasContext.closePath();
			canvasContext.stroke();
		}
	}

	prepareCanvas();

	const downloadBtn = document.createElement("A");
	downloadBtn.className = "modebar-btn";
	downloadBtn.rel = "tooltip";
	downloadBtn.dataset.title = "Download raw data";
	downloadBtn.dataset.toggle = "false";
	downloadBtn.dataset.gravity = "n";
	downloadBtn.innerHTML = "⬇️";
	// https://halistechnology.com/2015/05/28/use-javascript-to-export-your-data-as-csv/
	const _convertArrayOfObjectsToCSV = (arr) => {  
	    var result, ctr, keys, columnDelimiter, lineDelimiter;
	    columnDelimiter = ',';
	    lineDelimiter = '\n';
	    keys = Object.keys(arr[0]);
	    result = '';
	    result += keys.join(columnDelimiter);
	    result += lineDelimiter;
	    arr.forEach(function(item) {
	        ctr = 0;
	        keys.forEach(function(key) {
	            if (ctr > 0) result += columnDelimiter;

	            result += item[key];
	            ctr++;
	        });
	        result += lineDelimiter;
	    });
	    return result;
	};
	const _downloadCSV = (arr) => {  
	    var data, filename, link;
	    var csv = _convertArrayOfObjectsToCSV(arr);
	    if (csv == null)
	    	return;
	    filename = 'dataLab.csv';
	    if (!csv.match(/^data:text\/csv/i)) {
	        csv = 'data:text/csv;charset=utf-8,' + csv;
	    }
	    data = encodeURI(csv);
	    link = document.createElement('a');
	    link.setAttribute('href', data);
	    link.setAttribute('download', filename);
		link.dispatchEvent(new MouseEvent('click', {bubbles: true, cancelable: true, view: window}));
	};
	downloadBtn.addEventListener("click", () => {
		_downloadCSV(JSON.parse(
			document.getElementById("uploaded_fileAsJson").innerHTML
			));
	});

	const customizeDataBtn = document.createElement("A");
	customizeDataBtn.className = "modebar-btn";
	customizeDataBtn.rel = "tooltip";
	customizeDataBtn.dataset.title = "Show data settings";
	customizeDataBtn.dataset.toggle = "false";
	customizeDataBtn.dataset.gravity = "n";
	customizeDataBtn.innerHTML = "⚙️";
	let _showDataCustomization = false;
	const _dataCustomizationIds = [
		"datafieldselector_container",
		"selectDataFieldsPrompt", 
		"data_uploader_container",
		"selectDataGroupFieldsPrompt",
		"dataGroupFieldSelector_container",
		];
	customizeDataBtn.addEventListener("click", () => {
		if (_showDataCustomization) {
			_dataCustomizationIds.forEach(id => {
		 		document.getElementById(id).style.display = "none";
			});
		 	_showDataCustomization = false;
		 	customizeDataBtn.dataset.title = "Show data settings";
		} else {
			_dataCustomizationIds.forEach(id => {
		 		document.getElementById(id).style.display = "block";
			});
		 	_showDataCustomization = true;
		 	customizeDataBtn.dataset.title = "Hide data settings";
		}
	});

	const fullscreenbutton = document.createElement("A");
	fullscreenbutton.className = "modebar-btn";
	fullscreenbutton.rel = "tooltip";
	fullscreenbutton.dataset.title = "Enable full screen";
	fullscreenbutton.dataset.toggle = "false";
	fullscreenbutton.dataset.gravity = "n";
	fullscreenbutton.innerHTML = "📺";
	let originalGraphToWindowRatioWidth;
	let originalGraphToWindowRatioHeight;
	let _fullscreen = false;
		fullscreenbutton.addEventListener("click", () => {
		if (_fullscreen) {
			fullscreenbutton.dataset.title = "Enable full screen";
			 _fullscreen = false;
			 Plotly.relayout('graph', {
				 width: window.innerWidth*originalGraphToWindowRatioWidth,
				 height: window.innerHeight*originalGraphToWindowRatioHeight,
			 })
			 window.addEventListener('resize', () => {
				 Plotly.relayout('graph', {
					 width: window.innerWidth*originalGraphToWindowRatioWidth,
					 height: window.innerHeight*originalGraphToWindowRatioHeight,
				 })
			 })
			 svgContainer.style.backgroundColor = 'transparent';
		} else {
			const gd = document.getElementById('graph');
			originalGraphToWindowRatioWidth = gd._fullLayout.width/window.innerWidth;
			originalGraphToWindowRatioHeight = gd._fullLayout.height/window.innerHeight;
			const svgContainer = document.getElementsByClassName('svg-container')[0];
			svgContainer.style.backgroundColor = 'white';
			Plotly.relayout('graph', {
				width: window.innerWidth,
				height: window.innerHeight,
			  })
			  window.addEventListener('resize', () => {
				Plotly.relayout('graph', {
					width: window.innerWidth,
					height: window.innerHeight,
				});
			  })
			 _fullscreen = true;
			fullscreenbutton.dataset.title = "Disable full screen";
		}
	});

	const rangeToZeroButton = document.getElementById("rangeToZeroButton");
	rangeToZeroButton.className = "modebar-btn";
	rangeToZeroButton.rel = "tooltip";
	rangeToZeroButton.dataset.title = "Disable to-zero ranging";
	rangeToZeroButton.dataset.toggle = "false";
	rangeToZeroButton.dataset.gravity = "n";
	rangeToZeroButton.innerHTML = "0️⃣";
	const _rangeToZeroIndicator = document.getElementById("rangeToZeroIndicator");
	rangeToZeroButton.addEventListener("click", () => {
		if (_rangeToZeroIndicator.innerHTML === "true") {
			rangeToZeroButton.dataset.title = "Enable to-zero ranging";
		} else {
			rangeToZeroButton.dataset.title = "Disable to-zero ranging";
		}
	});

	const graphSlidersButton = document.getElementById("graphSlidersButton");
	graphSlidersButton.className = "modebar-btn";
	graphSlidersButton.rel = "tooltip";
	graphSlidersButton.dataset.title = "Show graph settings";
	graphSlidersButton.dataset.toggle = "false";
	graphSlidersButton.dataset.gravity = "n";
	graphSlidersButton.innerHTML = "📊";
	let _showGraphSlider = false;
	graphSlidersButton.addEventListener("click", () => {
		if (_showGraphSlider) {
		 	document.getElementById("graphTuning_slider_container").style.display = "none";
		 	_showGraphSlider = false;
			graphSlidersButton.dataset.title = "Show graph settings";
		} else {
		 	document.getElementById("graphTuning_slider_container").style.display = "block";
		 	_showGraphSlider = true;
			graphSlidersButton.dataset.title = "Hide graph settings";
		}
	});

	extraButtons = [customizeDataBtn, downloadBtn, graphSlidersButton, rangeToZeroButton, fullscreenbutton];
	$(document).on("mousemove", () => {
		if (!drawingIsAllowed()) {
			const buttons = document.querySelector(".modebar-group");
			if (buttons && !buttons.contains(extraButtons[0])) {
				extraButtons.forEach(button => buttons.appendChild(button));
			}
		}
	});