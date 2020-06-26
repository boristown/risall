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
	var delY = 50 + 300;

	//document.onmousedown = function () {
	//	flag = true;
	//	//获取需要删除的距离
	//	delX = event.clientX - animationdiv.offsetLeft;
	//	delY = event.clientY - animationdiv.offsetTop;
	//};

	//3.整个文档绑定鼠标移动事件
	document.onmousemove = function () {
		//if (flag) {
			//删除多余的距离 保持住按下的位置
			//var x = event.clientX - delX;
			var y = event.clientY - delY;
			//animationdiv.style.left = x + 'px';
			animationdiv.style.top = y + 'px';
		//}
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

        var data = data_tabs[tabindex - 1]


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