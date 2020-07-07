function init() {
	runHorseLight();
}
function runHorseLight() {
	let mylsTimer = null;
	if (mylsTimer != null) {
		clearInterval(mylsTimer);
	}
	var oUl = document.getElementById("appDonate");
	if (oUl != null) {
		oUl.innerHTML += oUl.innerHTML;
		oUl.innerHTML += oUl.innerHTML;
		oUl.innerHTML += oUl.innerHTML;
		var lis = oUl.getElementsByTagName('li');
		var lisTotalWidth = 0;
		var resetWidth = 0;
		for (var i = 0; i < lis.length; i++) {
			lisTotalWidth += lis[i].offsetWidth;
		}
		for (var i = 1; i <= lis.length / 4; i++) {
			resetWidth += lis[i].offsetWidth;
		}
		oUl.style.width = lisTotalWidth + 'px';
		var left = 0;
		mylsTimer = setInterval(function () {
			left -= 1;
			if (left <= -resetWidth) {
				left = 0;
			}
			oUl.style.left = left + 'px';
		}, 10)
	}
};

function initanimation() {
	//1.获取页面元素
	var animationdiv = document.querySelector('.animationdiv');
	//设置开关判断鼠标是在box否按下
	var flag = false;
	//2.box绑定鼠标按下事件
	//var delX = 50;
    var delY = mouseDis + canvasH;
    var delX = canvasW / 2.0;

	//document.onmousedown = function () {
	//	flag = true;
	//	//获取需要删除的距离
	//	delX = event.clientX - animationdiv.offsetLeft;
	//	delY = event.clientY - animationdiv.offsetTop;
	//};

	//3.整个文档绑定鼠标移动事件
	document.onmousemove = function () {
		var x = event.pageX - delX;
        var y = event.pageY - delY;
        var clientY = event.clientY;
        //显示在鼠标下方
        if (clientY < document.body.clientHeight / 2) {
            delY = - mouseDis;
        }
        //显示在鼠标上方
        else {
            delY = mouseDis + canvasH;
        };
        if (x < 0)
            x = 0;
        if (y < 0)
            y = 0;
        if (x > document.body.clientWidth - canvasW) {
            x = document.body.clientWidth - canvasW;
        };
		animationdiv.style.left = x + 'px';
		animationdiv.style.top = y + 'px';
	};

	////4.给整个文档绑定了 鼠标抬起事件
	//document.onmouseup = function () {
	//	flag = false;
	//};
};

var startdatestr = null;

function loadd3chart(data_tabs, data_dict, market_name, p_startdatestr) {

    startdatestr = p_startdatestr;

    var tooltip;
    var tooltipLines = [];
    var simulationsymbol;
    var simulationtitle;
    var simulationday;
    var simulationdate;
    var simulationbalance;
    //var width = 600, height = 300,
    var width = document.body.clientWidth;
    var height = 600;
    //var margin = { left: 100, top: 30, right: 100, bottom: 50 },
    var margin = { left: 0, top: 30, right: 0, bottom: 50 },
        g_width = width - margin.left - margin.right,
        g_height = height - margin.top - margin.bottom;
    //g_height = g_width / 2.0;

    tooltipLines = [];
    Date.prototype.Format = function (fmt) { //author: meizz
        var o = {
            "M+": this.getMonth() + 1, //月份
            "d+": this.getDate(), //日
            "h+": this.getHours(), //小时
            "m+": this.getMinutes(), //分
            "s+": this.getSeconds(), //秒
            "q+": Math.floor((this.getMonth() + 3) / 3), //季度
            "S": this.getMilliseconds() //毫秒
        };
        if (/(y+)/.test(fmt)) fmt = fmt.replace(RegExp.$1, (this.getFullYear() + "").substr(4 - RegExp.$1.length));
        for (var k in o)
            if (new RegExp("(" + k + ")").test(fmt)) fmt = fmt.replace(RegExp.$1, (RegExp.$1.length == 1) ? (o[k]) : (("00" + o[k]).substr(("" + o[k]).length)));
        return fmt;
    }

    //var data_dict = new Array()
    var scale_x_list = []
    var parseDate = d3.timeParse("%Y-%m-%d");
    var formatDate = d3.timeFormat("%Y-%m-%d");

    //循环添加TAB页面
    //for (var tabindex = 1; tabindex <= 3; tabindex++) {
    var tabindex = 1;
        ////svg
        //d3.select("#svg-tab" + tabindex).remove();
        //d3.select("#container-tab" + tabindex).append("svg")
        //    //width,height
        //    .attr("width", width)
        //    .attr("height", height)
        //    .attr("id", "svg-tab" + tabindex)

        //var g = d3.select("#svg-tab" + tabindex)
        d3.select("#pricesvgchart").selectAll("*").remove();

        var g = d3.select("#pricesvgchart")
            .attr("width", width)
            .attr("height", height)
            .append("g")
            .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

        //var data = {"2020-05-28": 30.5, "2020-05-29": 30.4, 5, 6, 8, 9, 3, 5, 2]

        var data = data_tabs[tabindex - 1];


        //for (var d in data) {
        //    d.key = parseDate(d.key);
        //}
        data.forEach(function (d) {
            d.date = (typeof (d.date) == 'string' ? parseDate(d.date) : d.date);
            d.close = +d.close;
            //d = parseDate(d)
        });
        //if (tabindex == 3) {
        //    var startdate = data[0].date
        //    //    data.forEach(function (d) {
        //    //        data_dict[d.date] = d;
        //    //    });
        //}
        //定义xy坐标轴的值域
        //var scale_x = d3.scaleLinear()
        var scale_x = d3.scaleTime()
            //.domain([0, data.length - 1])
            //.domain([d3.min(data[0]), d3.max(data[0])])
            //.domain([d3.min(data), d3.max(data)])
            .domain(d3.extent(data, function (d) { return d.date; }))
            .range([0, g_width]);
        scale_x_list.push(scale_x)
        //var scale_y = d3.scaleLinear()
        var scale_y = d3.scaleLog()
            //.exponent(2)
            //.domain([0, d3.max(data)])
            //.domain([d3.min(data[1]), d3.max(data[1])])
            //.domain([d3.min(data), d3.max(data)])
            .domain(d3.extent(data, function (d) { return d.close; }))
            .range([g_height, 0]);

        //var scale_balance = d3.scaleLinear()
        var scale_balance = d3.scaleLog()
            //.exponent(2)
            //.domain([0, d3.max(data)])
            //.domain([d3.min(data[1]), d3.max(data[1])])
            //.domain([d3.min(data), d3.max(data)])
            .domain(d3.extent(data, function (d) { return d.balance; }))
        .range([g_height, 0]);

    var scale_profit = d3.scaleLinear()
            .domain([0,d3.max(data, function (d) { return d.profit; })])
            .range([g_height, 0]);


        //画日收益函数data.Profit
      
        //画日收益
        g.append("g")
            .attr("class", "bars")
            .selectAll(".bar")
            .data(data).enter()
            .append("rect")
            .attr("class", "profitbar")
            .attr("x", function (d) { return scale_x(d.date); })
            .attr("width", g_width / data.length * 0.67)
            .attr("y", function (d) { return scale_profit(d.profit) > g_height ? g_height : scale_profit(d.profit); })
            .attr("height", function (d) {
                return Math.abs(g_height - scale_profit(d.profit));
            });
       

        //画面积函数
        var balance_area_generator = d3.area()
            .x(function (d, i) {
                //return scale_x(i);
                return scale_x(d.date);
            })
            .y0(g_height)
            .y1(function (d) {
                //return scale_y(d);
                return scale_balance(d.balance);
            })
            .curve(d3.curveMonotoneX)

        //画面积
        g.append("path")
            .attr("d", balance_area_generator(data)) //d="M1,0L20,40.....  d-path data
            .attr("class", "balanceerea")
        //.style("fill","#ff5017")

        //画面积函数
        var area_generator = d3.area()
            .x(function (d, i) {
                //return scale_x(i);
                return scale_x(d.date);
            })
            .y0(g_height)
            .y1(function (d) {
                //return scale_y(d);
                return scale_y(d.close);
            })
            .curve(d3.curveMonotoneX)

        //画面积
        g.append("path")
            .attr("d", area_generator(data)) //d="M1,0L20,40.....  d-path data
            .attr("class", "priceerea")
        //.style("fill","#ff5017")
        //定义X轴
        var xAxis = d3.axisBottom(scale_x)
            //.tickFormat(d3.time.format("%Y-%m-%d"))
            .tickFormat(d3.timeFormat("%Y-%m-%d"))

        //显示X轴
        g.append("g")
            .call(d3.axisBottom(scale_x))
            .attr("transform", "translate(0," + g_height + ")")
            .attr("fill", "transparent")

        //Y轴
        g.append("g")
            .call(d3.axisRight(scale_y))
            .attr("stroke-width","1")
            .attr("class", "price")

        //Y轴
        g.append("g")
            .call(d3.axisLeft(scale_balance))
            .attr("transform", "translate(" + g_width + ",0)")
            .attr("stroke-width", "1")
            .attr("class", "balance")

        //y轴文字
        g.append("text")
            .text("价格Price")
            .attr("transform", "rotate(-90)")
            .attr("class", "pricetext")
            //.attr("fill", "Turquoise")
            .attr("dy", "1em")
            .attr("text-anchor", "end")

        //y轴文字
        g.append("text")
            .text("余额Balance")
            .attr("transform", "translate(" + (g_width - 20) + ",0) rotate(-90)")
            .attr("class", "balancetext")
            .attr("dy", "1em")
            //.attr("fill", "DeepPink")
            .attr("text-anchor", "end")

        tooltip = d3.select('#tooltip');
        tooltipLine = g.append('line').attr('id', 'tooltipline' + tabindex);
        tooltipLines.push(tooltipLine);
        //tooltipLine                 = g.select('#tooltipline');
        simulationsymbol = d3.select('#simulationsymbol');
        simulationtitle = d3.select('#simulationtitle');
        simulationday = d3.select('#simulationday');
        simulationdate = d3.select('#simulationdate');
        simulationbalance = d3.select('#simulationbalance');

        //ToolTip Begin
        // Load the data and draw a chart
        let states, tipBox;

        tipBox = g.append('rect')
            .attr('width', g_width)
            .attr('height', g_height)
            .attr('opacity', 0)
            .datum(tabindex)
            .on('mousemove', drawTooltip_mouse)
            .on('mouseout', removeTooltip)
            .on('touchmove', drawTooltip_touch)
            .on('touchstart', drawTooltip_touch)
            .on('touchend', removeTooltip);

        // 非递归二分查找
        function binary_search(arr, key) {
            var low = 0,
                high = arr.length - 1;
            while (low <= high) {
                var mid = parseInt((high + low) / 2);
                if (Math.abs(key - arr[mid].date) / 1000 < 86400) {
                    return mid;
                } else if (key > arr[mid].date) {
                    low = mid + 1;
                } else if (key < arr[mid].date) {
                    high = mid - 1;
                } else {
                    return -1;
                }
            }
        };

        function removeTooltip(tabindex) {

            if (tooltip) tooltip.style('animation', 'fadeout10 0.5s')
                .style('opacity', 0);
            //if (tooltipLine) tooltipLine.attr('stroke', 'none');
            if (tooltipLines[tabindex - 1])
                tooltipLines[tabindex - 1]
                    .style('animation', 'fadeout06 0.5s')
                    .style('opacity', 0);
            if (simulationsymbol)
                simulationsymbol.style('opacity', 0)
                    .style('animation', 'fadeout10 0.5s');
            if (simulationtitle)
                simulationtitle.style('opacity', 0)
                    .style('animation', 'fadeout10 0.5s');
            if (simulationday)
                simulationday.style('opacity', 0)
                    .style('animation', 'fadeout10 0.5s');
            if (simulationdate)
                simulationdate.style('opacity', 0)
                    .style('animation', 'fadeout10 0.5s');
            if (simulationbalance)
                simulationbalance.style('opacity', 0)
                    .style('animation', 'fadeout10 0.5s');

            d3.selectAll("h1.hidewhensimulation")
                .style('opacity', 1)
                .style('animation', 'fadeoin10 0.5s')
            d3.selectAll("h2.hidewhensimulation")
                .style('opacity', 1)
                .style('animation', 'fadeoin10 0.5s')
            d3.selectAll("h3.hidewhensimulation")
                .style('opacity', 1)
                .style('animation', 'fadeoin10 0.5s')
            d3.selectAll("h4.hidewhensimulation")
                .style('opacity', 1)
                .style('animation', 'fadeoin10 0.5s')

        }

        function draw_date_tooltip(data, date, pageX, pageY, scale_X, tabindex) {

            //var seldata = data.find(d => Math.abs(d.date - date) / 1000 < 86400)
            //var dateindex = binary_search(data, date)
            //if (dateindex < 0)
            //    return;
            //var seldata = data[dateindex]
            var seldata = data_dict[date]

            //data.sort((a, b) => {
            //    return b.find(h => h.date == date).population - a.find(h => h.date == date).population;
            //})
            if (!seldata) return

            seldate = parseDate(seldata.date)
            startdate = parseDate(startdatestr)
            dayindex = (seldate - startdate) / (1000 * 60 * 60 * 24);

            //d3.select("h3.hidewhensimulation")
            //    .text(seldata.date + " 第" + dayindex + "天 Day " + dayindex)
            //
            //d3.select("h4.hidewhensimulation")
            //    .text("余额Balance: $" + Math.round(seldata.balance * 100) / 100)

            scaleX = scale_X(seldate)
            tooltipLines[tabindex - 1]
                .style('animation', 'fadein06 0.5s')
                .style('opacity', 0.6)
                //.style('display','block')
                .attr('x1', scaleX)
                .attr('x2', scaleX)
                .attr('y1', 0)
                .attr('y2', g_height);

            tooltip.html('<div id="tooltipprofit">' + seldata.profit + '%</div><div style="z-index:101"><h3 id="tooltipdate" align="left" >日期Date:' + seldata.date + '</h3><h3 id="tooltipprice" align="left">价格Price:' + seldata.close + '</h3><h3 id="tooltipbalance" align="left">余额Balance:' + Math.round(seldata.balance * 100) / 100 + '</h3><div>')
                .style('animation', 'fadein10 0.5s')
                .style('opacity', 1)
                //.style('left', d3.event.pageX + 20 + 'px')
                .style('left', pageX < width / 2 ? scaleX + 150 + 'px' : scaleX - 150 + 'px')
                .style('top', pageY - 200 + 'px')
                .selectAll()
            //.data(seldata).enter()

            simulationsymbol.text(market_name).style('opacity', 1)
                .style('animation', 'fadeoin10 0.5s')
            simulationtitle.text("AI模拟交易 AI Simulate Trading").style('opacity', 1)
                .style('animation', 'fadeoin10 0.5s')
            simulationday.text("第" + dayindex + "天 Day " + dayindex).style('opacity', 1)
                .style('animation', 'fadeoin10 0.5s')
            simulationdate.text("" + seldata.date).style('opacity', 1)
                .style('animation', 'fadeoin10 0.5s')
            simulationbalance.text("余额Balance:$" + Math.round(seldata.balance * 100) / 100).style('opacity', 1)
                .style('animation', 'fadeoin10 0.5s')

            d3.selectAll("h1.hidewhensimulation")
                .style('animation', 'fadeout10 0.5s')
                .style('opacity', 0)
            d3.selectAll("h2.hidewhensimulation")
                .style('animation', 'fadeout10 0.5s')
                .style('opacity', 0)
            d3.selectAll("h3.hidewhensimulation")
                .style('animation', 'fadeout10 0.5s')
                .style('opacity', 0)
            d3.selectAll("h4.hidewhensimulation")
                .style('animation', 'fadeout10 0.5s')
                .style('opacity', 0)

        }

        function drawTooltip_mouse(d, i) {

            //const date = Math.floor((scale_x.invert(d3.mouse(tipBox.node())[0]) + data.length/2) / data.length);

            tabindex = d

            data = data_tabs[tabindex - 1]

            const date = scale_x_list[tabindex - 1].invert(d3.mouse(tipBox.node())[0]);

            var scale_X = scale_x_list[tabindex - 1]

            draw_date_tooltip(data, formatDate(date), d3.event.pageX, d3.event.pageY, scale_X, tabindex)
        }

        function drawTooltip_touch(d, i) {

            d3.event.preventDefault();
            d3.event.stopPropagation();

            tabindex = d

            data = data_tabs[tabindex - 1]

            var touchpoint = d3.touches(this)[0]
            var pagex = d3.event.changedTouches[0].pageX
            var pagey = d3.event.changedTouches[0].pageY
            var scale_date = scale_x_list[tabindex - 1]

            var date = scale_date.invert(touchpoint[0]);

            var scale_X = scale_x_list[tabindex - 1]


            draw_date_tooltip(data, formatDate(date), pagex, pagey, scale_X, tabindex)
        }
    //}

    function $(id) {
        return typeof id === "string" ? document.getElementById(id) : document;
    };


    //window.onload = function () {
    //    //初始化计时器;
    //    var timer = null;
    //    //初始化索引;
    //    var index = -1;
    //    var items = $("list").getElementsByTagName("li");
    //    var divs = $("item").getElementsByTagName("div");

    //    //循环遍历标题名和内容盒子;
    //    for (var i = 0, len = items.length; i < len; i++) {
    //        items[i].id = i;
    //        items[i].onmouseover = switchbox;
    //        items[i].ontouchstart = switchbox;
    //    }

    //    function switchbox() {
    //        for (var j = 0, len = items.length; j < len; j++) {
    //            items[j].className = "unselect";
    //            divs[j].style.display = "none";
    //        }
    //        this.className = "select";
    //        divs[this.id].style.display = "block";
    //    }

    //}
};

//读取url参数
function getQueryVariable(variable) {
    var query = window.location.search.substring(1);
    var vars = query.split("&");
    for (var i = 0; i < vars.length; i++) {
        var pair = vars[i].split("=");
        if (pair[0] == variable) { return pair[1]; }
    }
    return (false);
}

//粒子连接特效
function particleConnector() {
    const canvas = document.querySelector('.fullscreenanimation').querySelector('canvas');
    const ctx = canvas.getContext('2d');

    const RESOLUTION = 1;

    //let w = canvas.width = window.innerWidth * RESOLUTION;
    //let h = canvas.height = window.innerHeight * RESOLUTION;
    let w = canvas.width = document.body.scrollWidth * RESOLUTION;
    let h = canvas.height = document.body.scrollHeight * RESOLUTION;

    const PARTICLE_COUNT = 400;
    const CONNECT_DISTANCE = w * 0.05;
    const FORCE_DISTANCE = w * 0.1;

    const r = (n = 1) => Math.random() * n;
    const PI = Math.PI;
    const TAU = PI * 2;

    let time = new Date();

    const lerp = (start, end, amt) => {
        return (1 - amt) * start + amt * end;
    };

    const distance = (x1, y1, x2, y2) => {
        const a = x1 - x2;
        const b = y1 - y2;
        return Math.sqrt(a * a + b * b);
    };

    const angle = (cx, cy, ex, ey) => {
        return Math.atan2(ey - cy, ex - cx);
    };

    const particlePrototype = () => ({
        x: w * 0.5 + Math.cos(r(TAU)) * r(w * 0.5),
        y: h * 0.5 + Math.sin(r(TAU)) * r(h * 0.5),
        angle: r(TAU),
        speed: r(0.15),
        normalSpeed: r(0.15),
        oscAmplitudeX: r(2),
        oscSpeedX: 0.001 + r(0.008),
        oscAmplitudeY: r(2),
        oscSpeedY: 0.001 + r(0.008),
        connectDistance: r(CONNECT_DISTANCE),
        color: {
            r: Math.round(200 + r(55)),
            g: Math.round(150 + r(105)),
            b: Math.round(200 + r(55))
        }
    });



    const particles = new Array(PARTICLE_COUNT).
        fill({}).
        map(particlePrototype);

    const update = () => {
        particles.forEach(p1 => {
            p1.x += (Math.cos(p1.angle) + Math.cos(time * p1.oscSpeedX) * p1.oscAmplitudeX) * p1.speed;
            p1.y += (Math.sin(p1.angle) + Math.cos(time * p1.oscSpeedY) * p1.oscAmplitudeY) * p1.speed;

            p1.speed = lerp(p1.speed, p1.normalSpeed * RESOLUTION, 0.1);

            if (p1.x > w || p1.x < 0) {
                p1.angle = PI - p1.angle;
            }
            if (p1.y > h || p1.y < 0) {
                p1.angle = -p1.angle;
            }

            if (r() < 0.005)
                p1.oscAmplitudeX = r(2);
            if (r() < 0.005)
                p1.oscSpeedX = 0.001 + r(0.008);
            if (r() < 0.005)
                p1.oscAmplitudeY = r(2);
            if (r() < 0.005)
                p1.oscSpeedY = 0.001 + r(0.008);

            p1.x = Math.max(-0.01, Math.min(p1.x, w + 0.01));
            p1.y = Math.max(-0.01, Math.min(p1.y, h + 0.01));
        });
    };

    const render = () => {

        ctx.clearRect(0, 0, w, h);

        particles.map(p1 => {
            particles.
                filter(p2 => {
                    if (p1 == p2)
                        return false;
                    if (distance(p1.x, p1.y, p2.x, p2.y) > p1.connectDistance)
                        return false;
                    return true;
                }).
                map(p2 => {
                    const dist = distance(p1.x, p1.y, p2.x, p2.y);
                    p1.speed = lerp(p1.speed, p1.speed + 0.05 / p1.connectDistance * dist, 0.2);
                    return {
                        p1,
                        p2,
                        color: p1.color,
                        opacity: Math.floor(100 / p1.connectDistance * (p1.connectDistance - dist)) / 100
                    };

                }).
                forEach((line, i) => {
                    const colorSwing = Math.sin(time * line.p1.oscSpeedX);
                    ctx.beginPath();
                    ctx.globalAlpha = line.opacity;
                    ctx.moveTo(line.p1.x, line.p1.y);
                    ctx.lineTo(line.p2.x, line.p2.y);
                    ctx.strokeStyle = `rgb(
					${Math.floor(line.color.r * colorSwing)},
					${Math.floor(line.color.g * 0.5 + line.color.g * 0.5 * colorSwing)},
					${line.color.b}
				)`;
                    ctx.lineWidth = line.opacity * 4;
                    ctx.stroke();
                    ctx.closePath();
                });
        });

    };

    const loop = () => {
        time = new Date();
        update();
        render();
        window.requestAnimationFrame(loop);
    };

    loop();

    window.addEventListener('mousemove', e => {

        //const mouseX = e.layerX * RESOLUTION;
        //const mouseY = e.layerY * RESOLUTION;
        const mouseX = e.pageX * RESOLUTION;
        const mouseY = e.pageY * RESOLUTION;

        particles.forEach(p => {
            const dist = distance(mouseX, mouseY, p.x, p.y);

            if (dist < FORCE_DISTANCE && dist > 0) {
                p.angle = angle(mouseX, mouseY, p.x, p.y);
                const force = (FORCE_DISTANCE - dist) * 0.1;
                p.speed = lerp(p.speed, force, 0.2);
            }
        });

    });

    window.addEventListener('resize', e => {
        //w = canvas.width = window.innerWidth * RESOLUTION;
        //h = canvas.height = window.innerHeight * RESOLUTION;
        w = canvas.width = document.body.scrollWidth * RESOLUTION;
        h = canvas.height = document.body.scrollHeight * RESOLUTION;
    });
};

//月份字典
var monthDict = {
    "01": 'Jan.',
    "02": 'Feb.',
    "03": 'Mar.',
    "04": 'Apr.',
    "05": 'May',
    "06": 'June',
    "07": 'July',
    "08": 'Aug.',
    "09": 'Sept.',
    "10": 'Oct.',
    "11": 'Nov.',
    "12": 'Dec.',
};

function clearItemFrame(item, itemindex, tableitems) {
    let canvas = document.getElementById('itemaninationcanvas'); //画布
    let ctx = canvas.getContext('2d'); //绘画上下文
    ctx.clearRect(0, 0, canvas.width, canvas.height); //清空
}

function drawItemFrame(item, itemindex, tableitems) {

    let canvas = document.getElementById('itemaninationcanvas'); //画布
    let ctx = canvas.getContext('2d'); //绘画上下文
    let balance = parseFloat(item.Balance); //当前余额
    let atr = parseFloat(item.ATR); //ATR百分数
    let entryposition = balance / atr; //头寸金额
    let entryprice = parseFloat(item.Close); //入场价格
    let isBuy = (item.Prediction.indexOf("Buy") != -1); //是否是做多
    let entryquantity = entryposition / entryprice; //头寸数量
    let entrydate = item.Date; // 入场日期
    let exitprice = item.StopPrice; //离场价格
    let exitdate = item.StopDate; //离场日期
    let exitposition = entryquantity * exitprice; //离场头寸金额
    let profitamount = isBuy ? exitposition - entryposition : entryposition - exitposition; //盈利金额

    clientW = parseInt(document.body.clientWidth);
    canvas.setAttribute("width", canvasW)
    canvas.setAttribute("height", canvasH)

    ctx.clearRect(0, 0, canvas.width, canvas.height); //清空

    if (exitdate == '-')
        return;

    let priceCurveList = [];

    let minPrice = Infinity;
    let maxPrice = 0;
    let countPrice = 0;
    let lastC = 0;

    //整理市场价格曲线数据
    for (let endindex = itemindex; endindex >= 0; endindex--) {
        let dayItem = tableitems[endindex];
        if (endindex == itemindex)
            lastC = dayItem["Close"];
        priceCurveList.push(dayItem);
        countPrice++;
        //更新最低价
        if (lastC < dayItem["Low"]) {
            dayItem["Low"] = lastC;
        };
        //更新最高价
        if (lastC > dayItem["High"]) {
            dayItem["High"] = lastC;
        };
        //计算最低价
        if (dayItem["Low"] < minPrice) {
            minPrice = dayItem["Low"];
        };
        //计算最高价
        if (dayItem["High"] > maxPrice) {
            maxPrice = dayItem["High"];
        };
        if (dayItem["Date"] == exitdate)
            break;
        lastC = dayItem["Close"];
    };

    let rangePrice = maxPrice - minPrice;
    let priceScale = 1.0;
    let scaledRangePrice = rangePrice;
    //原创的价格拉伸算法
    while (scaledRangePrice < 10 || scaledRangePrice > 99) {
        if (scaledRangePrice < 10) {
            priceScale *= 10.0;
            scaledRangePrice *= 10.0;
        }
        else if(scaledRangePrice > 99){
            priceScale /= 10.0;
            scaledRangePrice /= 10.0;
        };
    };
    let leftMargin = 30;
    let rightMargin = 30;

    //每天的宽度
    let dayW = (canvasW - leftMargin - rightMargin) / (countPrice == 1 ? 1 : ( countPrice - 1 ));

    //图层	内容
    //1	600px * 600px画布，背景纯黑（做空）或纯白（做多）。
    //2	对于天数N，绘制N - 1条1px灰色竖线，将画面分割为N份，左侧预留30px空间，用于显示价格。
    //3	将画布下方30px、上方30px高度覆盖为背景色。
    //4	在图层2每根竖线的下方，图层3的位置上输出日、月或年，文字为背景反色。
    //5	使用[日期，最高价]和[日期，最低价]序列绘制一条从皇家蓝到暗绿宝石的水平渐变通道，通道内部50 % 透明度。
    //6	使用[日期，收盘价]序列绘制一条背景反色的折线，30 % 透明度。
    //7	在入场[日期, 价格]的坐标上绘制一个浅灰（黑色背景时）或深灰（白色背景时）的10px直径实心圆A。
    //8	在图层5实心圆左边的位置显示买入Buy或卖出Sell价XXX，使用背景色的反色，使用图层15的规则来显示价格。
    //9	在离场日期, 价格]的坐标上绘制一个OrangeRed橙红色（亏损时）或LimeGreen闪光深绿（盈利时）的10px直径实心圆B。
    //10 在图层7实心圆右边的位置显示卖出Sell或买入Buy价XXX，使用背景色的反色，使用图层15的规则来显示价格。
    //11	找到图表中未绘制图形的且距离实心圆A最近的高度150 * 宽度300的矩形区域，设置为实心圆A的同色背景。
    //12	找到图表中未绘制图形的且距离实心圆B最近的高度150 * 宽度300的矩形区域，设置为实心圆B的同色背景。
    //13	在图层11上显示“AI预测XX评分XX触发做多 / 做空，ATR = XX %”，在图层12上显示“从价格XX下跌1倍ATR触发止损，盈利 / 亏损=XX %“，只显示2位有效数字。
    //14	在图表上方，图层3的位置上显示：”海龟三号交易系统：头寸大小 = 余额 * 1 % /ATR，当移动亏损达到余额的1%时触发强制止损“，文字为背景反色。
    //15	在图表左侧预留的区域显示价格，价格只显示发生变化的最高3位数。例如价格范围9702到10213显示为97到102; 价格范围0.00345到0.00356显示为45到56。
    //16	在图表下方显示一条横线和N条短竖线作为日期坐标轴，使用浅灰（黑色背景时）或深灰（白色背景时）。
    //17	在图表左方显示一条竖线和N条短横线作为价格坐标轴，使用浅灰（黑色背景时）或深灰（白色背景时）。

    //图层1: 600px * 600px画布，背景纯黑（做空）或纯白（做多）。
    let canvasBgColor = isBuy ? '#ffffff' : '#000000'
    let canvasColor = isBuy ? '#000000' : '#ffffff'
    let canvasMinorLineColor = '#808080';
    let canvasColorGray = isBuy ? '#696969' : '#D3D3D3'
    ctx.fillStyle = isBuy ? '#ffffff' : '#000000'
    ctx.fillRect(0, 0, canvasW, canvasH);

    //图层2: 对于天数N，绘制N-1条1px灰色竖线，将画面分割为N份，左侧预留30px空间，用于显示价格。
    ctx.fillStyle = canvasMinorLineColor;

    //计算X坐标
    function getPositionX(dayindex) {
        return leftMargin + dayW * dayindex;
    };

    for (let priceindex = 1; priceindex < countPrice; priceindex++) {
        ctx.fillRect(getPositionX(priceindex), 0, 1, canvasH);
    };
    let topMargin = 35;
    let bottomMargin = 35;

    ctx.fillStyle = canvasColorGray;
    ctx.fillRect(getPositionX(0), 0, 1, canvasH);
    ctx.fillRect(0, canvasH - bottomMargin, canvasW, 1);

    //图层3: 将画布下方30px、上方30px高度覆盖为背景色。

    ctx.fillStyle = canvasBgColor;
    ctx.fillRect(0, 0, canvasW, topMargin);
    ctx.fillRect(0, canvasH - bottomMargin - 1, canvasW, bottomMargin);

    //图层4: 在图层2每根竖线的下方，图层3的位置上输出日、月或年，文字为背景反色。
    ctx.fillStyle = canvasColor;
    ctx.font = "12px serif";
    let fontHeight = 13;
    for (let priceindex = 0; priceindex < countPrice; priceindex++) {
        let dateText = priceCurveList[priceindex]["Date"];
        let dateElements = dateText.split("-");
        if (dateElements.length != 3)
            return;
        let dateElementText = "";
        if (dateElements[1] == '01' && dateElements[2] == '01') //显示为年
            dateElementText = dateElements[0];
        else if (dateElements[2] == '01') //显示为月
            dateElementText = monthDict[dateElements[1]];
        else //显示为日
            dateElementText = dateElements[2];
        ctx.fillText(dateElementText, getPositionX(priceindex) - (fontHeight * dateElementText.length) / 4, canvasH - bottomMargin + fontHeight);
    };
    

    //计算Y坐标
    function getPositionY(price) {
        return topMargin + (canvasH - topMargin - bottomMargin) / rangePrice * (maxPrice - price);
    };

    //图层5: 使用[日期，最高价]和[日期，最低价]序列绘制一条从皇家蓝到暗绿宝石的水平渐变通道，通道内部50% 透明度。
    let canvasGradientColorBegin = '#3AB8A0';
    let canvasGradientColorCenter = '#2C92A1';
    let canvasGradientColorEnd = '#1E6A9E';

    ctx.beginPath();
    ctx.globalAlpha = "0.5";
    let grd = ctx.createLinearGradient(leftMargin, 0, canvasW - rightMargin, 0);
    grd.addColorStop(0, canvasGradientColorBegin);
    grd.addColorStop(0.5, canvasGradientColorCenter);
    grd.addColorStop(1, canvasGradientColorEnd);
    ctx.fillStyle = grd;
    ctx.moveTo(getPositionX(0), getPositionY(priceCurveList[0]["Low"]));
    let maxDistance = 0;
    let currentLocationX = 0;
    let currentLocationY = 0;
    let textLocationX = 0;
    let textLocationY = 0;
    let currentDistance = 0;
    for (let priceindex = 0; priceindex < countPrice; priceindex++) {
        currentLocationX = getPositionX(priceindex);
        currentLocationY = getPositionY(priceCurveList[priceindex]["High"]);
        ctx.lineTo(currentLocationX, currentLocationY);
        currentDistance = maxPrice - priceCurveList[priceindex]["High"];
        if (currentDistance > maxDistance) {
            maxDistance = currentDistance;
            textLocationX = currentLocationX;
            textLocationY = getPositionY(maxPrice);
        };
    };
    for (let priceindex = countPrice - 1; priceindex >= 0; priceindex--) {
        currentLocationX = getPositionX(priceindex);
        currentLocationY = getPositionY(priceCurveList[priceindex]["Low"]);
        ctx.lineTo(currentLocationX, currentLocationY);
        currentDistance = priceCurveList[priceindex]["Low"] - minPrice;
        if (currentDistance > maxDistance) {
            maxDistance = currentDistance;
            textLocationX = currentLocationX;
            textLocationY = getPositionY(minPrice);
        };
    };
    ctx.fill();

    //图层6：使用[日期，收盘价]序列绘制一条背景反色的折线，30 % 透明度。
    ctx.beginPath();
    ctx.lineWidth = 3;
    ctx.strokeStyle = canvasColor;
    ctx.globalAlpha = "0.5";
    ctx.moveTo(getPositionX(0), getPositionY(priceCurveList[0]["Close"]));
    for (let priceindex = 0; priceindex < countPrice; priceindex++) {
        ctx.lineTo(getPositionX(priceindex), getPositionY(priceCurveList[priceindex]["Close"]));
    };
    ctx.stroke();

    ctx.globalAlpha = "1";
    //图层7: 在入场[日期,价格]的坐标上绘制一个浅灰（黑色背景时）或深灰（白色背景时）的10px直径实心圆A。
    let positionX = getPositionX(0);
    let positionY = getPositionY(priceCurveList[0]["Close"]);

    ctx.beginPath();
    ctx.fillStyle = canvasColorGray;
    ctx.arc(positionX, positionY, 5.0, 0, Math.PI * 2, false);
    ctx.fill();

    //图层8: 在图层5实心圆左边的位置显示买入Buy或卖出Sell价XXX，使用背景色的反色，使用图层15的规则来显示价格。
    function priceFormart(price) {
        return Math.round(price * priceScale);
    };
    ctx.fillStyle = canvasColor;
    ctx.fillText(priceFormart(priceCurveList[0]["Close"]), 2, positionY + fontHeight / 2);

    //图层9: 在离场日期, 价格]的坐标上绘制一个OrangeRed橙红色（亏损时）或LimeGreen闪光深绿（盈利时）的10px直径实心圆B。
    positionX = getPositionX(countPrice-1);
    positionY = getPositionY(priceCurveList[0]["StopPrice"]);

    let cancasWinColor = profitamount < 0 ? '#f22e2e' : '#34d937';

    ctx.beginPath();
    ctx.fillStyle = cancasWinColor;
    ctx.arc(positionX, positionY, 5.0, 0, Math.PI * 2, false);
    ctx.fill();

    //图层10: 在图层7实心圆右边的位置显示卖出Sell或买入Buy价XXX，使用背景色的反色，使用图层15的规则来显示价格。
    ctx.fillStyle = canvasColor;
    ctx.fillText(priceFormart(priceCurveList[0]["StopPrice"]), positionX + 7, positionY + fontHeight / 2);

    //11	找到图表中未绘制图形的且距离实心圆A最近的高度150 * 宽度300的矩形区域，设置为实心圆A的同色背景。
    //12	找到图表中未绘制图形的且距离实心圆B最近的高度150 * 宽度300的矩形区域，设置为实心圆B的同色背景。

    ctx.globalAlpha = "0.5";
    ctx.fillStyle = cancasWinColor;

    textRectW = 300;
    textRectH = 200;
    textRectLeft = textLocationX - textRectW / 2.0;
    textRectTop = textLocationY - textRectH / 2.0;
    if (textRectLeft < 0) textRectLeft = 0;
    if (textRectTop < 0) textRectTop = 0;
    if (textRectLeft + textRectW > canvasW) textRectLeft = canvasW - textRectW;
    if (textRectTop + textRectH > canvasH - bottomMargin) textRectTop = canvasH - bottomMargin - textRectH;

    ctx.font = "80px serif";
    fontHeight = 80;
    //ctx.fillRect(textRectLeft, textRectTop, textRectW, textRectH);
    ctx.fillText(item.Profit, textRectLeft, textRectTop + fontHeight + 50);
    //13	在图层11上显示“AI预测XX评分XX触发做多 / 做空，ATR = XX %”，在图层12上显示“从价格XX下跌1倍ATR触发止损，盈利 / 亏损=XX %“，只显示2位有效数字。
    let textLeft = 2;

    ctx.font = "12px serif";
    fontHeight = 13;
    ctx.globalAlpha = "1";
    ctx.fillStyle = canvasColor;
    ctx.fillText("AI指令:" +item.Prediction + " ATR:" + item["ATR"].toString(), textRectLeft + textLeft, textRectTop + fontHeight, textRectW);
    ctx.fillText("盈亏Profit: " + item.Profit, textRectLeft + textLeft, textRectTop + fontHeight * 2.5, textRectW);
    ctx.fillText("入场Cost: " + priceFormart(item["Close"]) + " => 离场Stop: " + priceFormart(item["StopPrice"]) + " [x" + priceScale.toString() + "]", textRectLeft + textLeft, textRectTop + fontHeight * 4, textRectW);
    ctx.fillText("海龟三号AI交易系统：", textRectLeft + textLeft, textRectTop + fontHeight * 5.5, textRectW);
    ctx.fillText("Turtle No.3 AI Trading System:", textRectLeft + textLeft, textRectTop + fontHeight * 7, textRectW);
    ctx.fillText("头寸大小 = 余额 * 1 % / ATR；", textRectLeft + textLeft, textRectTop + fontHeight * 8.5, textRectW);
    ctx.fillText("Position = balance * 1% / ATR;", textRectLeft + textLeft, textRectTop + fontHeight * 10, textRectW);
    ctx.fillText("当移动亏损达到余额的1%时触发强制止损。", textRectLeft + textLeft, textRectTop + fontHeight * 11.5, textRectW);
    ctx.fillText("Moving stop is triggered when loss reaches 1%.", textRectLeft + textLeft, textRectTop + fontHeight *13, textRectW);
    

    //let lastX = 0;
    //let lastH = canvasH;
    //let lastL = canvasH;
    //let lastC = canvasH;
    //for (let priceindex = 0; priceindex < countPrice; priceindex++) {
    //    currX = getPositionX(priceindex);
    //    currH = getPositionY(priceCurveList[priceindex]["High"]);
    //    currL = getPositionY(priceCurveList[priceindex]["Low"]);
    //    currC = getPositionY(priceCurveList[priceindex]["Close"]);
    //};

    
    //fontH = 20; //字体高度
    //barH = 30; //横条高度
    //spanW = 5; //宽度间隔
    //spanH = 5; //高度间隔
    //spanL = (clientW - longwidth) / 2.0; //左间隔
    //ctx.fillStyle = isBuy ? buyStyle : sellStyle;
    //curY = spanH;
    //ctx.fillText(entrydate + " 入场Entry：" + item.Prediction, spanL, curY + fontH);
    //curY += fontH + spanH;
    //ctx.fillRect(spanL, curY, entryposition > exitposition ? longwidth : shortwidth, barH);
    //ctx.fillStyle = bartextStyle;
    //if (entryposition <= exitposition) {
    //    ctx.fillText((!isBuy ? "亏损Loss: $" : "盈利Win: $") + profitamount, spanL + shortwidth + spanW, curY + fontH);
    //};
    ////ctx.fillText("数量Qty:" + entryquantity + " * 价格Price:$" + entryprice + " =  金额Amt:$" + entryposition, spanL, curY + fontH);
    //ctx.fillText((isBuy ? "支出Expenses " : "收入Income ") + "金额Amt:$" + entryposition, spanL, curY + fontH);

    //curY += barH + spanH;
    //ctx.fillStyle = isBuy ? sellStyle : buyStyle;
    //ctx.fillText(exitdate + " 退出Exit：" + item.Prediction, spanL, curY + fontH);
    //curY += fontH + spanH;
    //ctx.fillRect(spanL, curY, entryposition > exitposition ? shortwidth : longwidth, barH);
    //ctx.fillStyle = bartextStyle;
    //if (entryposition > exitposition) {
    //    ctx.fillText((isBuy ? "亏损Loss: $" : "盈利Win: $") + profitamount, spanL + shortwidth + spanW, curY + fontH);
    //};
    ////ctx.fillText("数量Qty:" + entryquantity + " * 价格Price:$" + exitprice + " =  金额Amt:$" + exitposition, spanL, curY + fontH);
    //ctx.fillText((isBuy ? "收入Income " : "支出Expenses ") + "金额Amt:$" + exitposition, spanL, curY + fontH);
};


function marketOrientationChange() {
    //如果宽度>=高度，就显示电脑界面
    if (window.innerWidth >= window.innerHeight) {
        expandMarketTable();
    }
    //如果宽度<高度，就显示手机界面
    else {
        collapseMarketTable();
    };
    loadd3chart(g_data_tabs, g_data_dict, g_market_name, g_startdate);
};

//折叠TABLE
function collapseMarketTable() {
    var tab = document.getElementById("MarketTable");
    var trs = tab.rows;
    for (let i = 0, len = trs.length; i < len; i++) {
        trs[i].cells[1].style.display = 'none';
        trs[i].cells[2].style.display = 'none';
        trs[i].cells[3].style.display = 'none';
        trs[i].cells[4].style.display = 'none';
        trs[i].cells[5].style.display = 'none';
        trs[i].cells[6].style.display = 'none';
        trs[i].cells[7].style.display = 'none';
        trs[i].cells[8].style.display = 'none';
        trs[i].cells[9].style.display = 'none';
        trs[i].cells[10].style.display = 'none';
    }
};

//展开TABLE
function expandMarketTable() {
    var tab = document.getElementById("MarketTable");
    var trs = tab.rows;
    for (let i = 0, len = trs.length; i < len; i++) {
        trs[i].cells[1].style.display = '';
        trs[i].cells[2].style.display = '';
        trs[i].cells[3].style.display = '';
        trs[i].cells[4].style.display = '';
        trs[i].cells[5].style.display = '';
        trs[i].cells[6].style.display = '';
        trs[i].cells[7].style.display = '';
        trs[i].cells[8].style.display = '';
        trs[i].cells[9].style.display = '';
        trs[i].cells[10].style.display = '';
    }
};