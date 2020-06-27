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
        if (x < 0)
            x = 0;
        if (y < 0)
            y = 0;
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
    var margin = { left: 100, top: 30, right: 100, bottom: 20 },
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
            d.date = parseDate(d.date);
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

        //定义X轴
        var xAxis = d3.axisBottom(scale_x)
            //.tickFormat(d3.time.format("%Y-%m-%d"))
            .tickFormat(d3.timeFormat("%Y-%m-%d"))

        //显示X轴
        g.append("g")
            .call(d3.axisBottom(scale_x))
            .attr("transform", "translate(0," + g_height + ")")
            .attr("fill", "#48D1CC")

        //Y轴
        g.append("g")
            .call(d3.axisLeft(scale_y))
            .attr("class", "price")

        //Y轴
        g.append("g")
            .call(d3.axisRight(scale_balance))
            .attr("transform", "translate(" + g_width + ",0)")
            .attr("class", "balance")

        //y轴文字
        g.append("text")
            .text("价格Price")
            .attr("transform", "rotate(-90)")
            .attr("fill", "Turquoise")
            .attr("dy", "1em")
            .attr("text-anchor", "end")

        //y轴文字
        g.append("text")
            .text("余额Balance")
            .attr("transform", "translate(" + (g_width - 20) + ",0) rotate(-90)")
            .attr("dy", "1em")
            .attr("fill", "DeepPink")
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

            tooltip.html('<h3 id="tooltipdate" align="left" >日期Date:' + seldata.date + '</h3><h3 id="tooltipprice" align="left">价格Price:' + seldata.close + '</h3><h3 id="tooltipbalance" align="left">余额Balance:' + Math.round(seldata.balance * 100) / 100 + '</h3>')
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
    }

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

    let priceCurveList = []

    let minPrice = Infinity;
    let maxPrice = 0;
    let countPrice = 0;

    //整理市场价格曲线数据
    for (let endindex = itemindex; endindex >= 0; endindex--) {
        let dayItem = tableitems[endindex];
        priceCurveList.append(dayItem);
        countPrice++;
        if (dayItem["Low"] < minPrice) {
            minPrice = dayItem["Low"];
        }
        if (dayItem["High"] > maxPrice) {
            maxPrice = dayItem["High"];
        }
    }

    let rangePrice = maxPrice - minPrice;

    //计算价格的Y坐标
    function getPriceY(price) {
        return canvasH 
    }

    //每天的宽度
    dayW = clientW / (countPrice + 1);


    ctx.font = "16px serif";
    fontH = 20; //字体高度
    barH = 30; //横条高度
    spanW = 5; //宽度间隔
    spanH = 5; //高度间隔
    spanL = (clientW - longwidth) / 2.0; //左间隔
    ctx.fillStyle = isBuy ? buyStyle : sellStyle;
    curY = spanH;
    ctx.fillText(entrydate + " 入场Entry：" + item.Prediction, spanL, curY + fontH);
    curY += fontH + spanH;
    ctx.fillRect(spanL, curY, entryposition > exitposition ? longwidth : shortwidth, barH);
    ctx.fillStyle = bartextStyle;
    if (entryposition <= exitposition) {
        ctx.fillText((!isBuy ? "亏损Loss: $" : "盈利Win: $") + profitamount, spanL + shortwidth + spanW, curY + fontH);
    };
    //ctx.fillText("数量Qty:" + entryquantity + " * 价格Price:$" + entryprice + " =  金额Amt:$" + entryposition, spanL, curY + fontH);
    ctx.fillText((isBuy ? "支出Expenses " : "收入Income ") + "金额Amt:$" + entryposition, spanL, curY + fontH);

    curY += barH + spanH
    ctx.fillStyle = isBuy ? sellStyle : buyStyle;
    ctx.fillText(exitdate + " 退出Exit：" + item.Prediction, spanL, curY + fontH);
    curY += fontH + spanH;
    ctx.fillRect(spanL, curY, entryposition > exitposition ? shortwidth : longwidth, barH);
    ctx.fillStyle = bartextStyle;
    if (entryposition > exitposition) {
        ctx.fillText((isBuy ? "亏损Loss: $" : "盈利Win: $") + profitamount, spanL + shortwidth + spanW, curY + fontH);
    };
    //ctx.fillText("数量Qty:" + entryquantity + " * 价格Price:$" + exitprice + " =  金额Amt:$" + exitposition, spanL, curY + fontH);
    ctx.fillText((isBuy ? "收入Income " : "支出Expenses ") + "金额Amt:$" + exitposition, spanL, curY + fontH);
};