(function(){
    var reduce = matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches;

    /* parallax on video */
    var hero = document.getElementById("heroTpl"), bg = document.getElementById("bgVideo");
    if(bg && !reduce){
        var t=false, mx=0, my=0;
        hero.addEventListener("mousemove", function(e){
            var r=hero.getBoundingClientRect();
            mx=((e.clientX-r.left)/r.width-0.5)*2; my=((e.clientY-r.top)/r.height-0.5)*2;
            if(!t){ requestAnimationFrame(function(){ bg.style.setProperty("--pan","translate("+(mx*-14)+"px,"+(my*-10)+"px)"); t=false; }); t=true; }
        });
    }

    /* glass slider */
    var track=document.getElementById("track"), slides=[].slice.call(track.querySelectorAll(".tpl-slide"));
    var dotsWrap=document.getElementById("dots"), cur=0, timer=null;
    slides.forEach(function(_,i){ var d=document.createElement("span"); d.className="dot"+(i===0?" active":""); d.onclick=function(){ go(i); restart(); }; dotsWrap.appendChild(d); });
    var dots=[].slice.call(dotsWrap.querySelectorAll(".dot"));
    function go(i){ slides[cur].classList.remove("active"); dots[cur].classList.remove("active"); cur=(i+slides.length)%slides.length; slides[cur].classList.add("active"); dots[cur].classList.add("active"); }
    function start(){ timer=setInterval(function(){ go(cur+1); },5000); }
    function stop(){ clearInterval(timer); }
    function restart(){ stop(); start(); }
    document.getElementById("next").onclick=function(){ go(cur+1); restart(); };
    document.getElementById("prev").onclick=function(){ go(cur-1); restart(); };
    document.getElementById("slider").addEventListener("mouseenter",stop);
    document.getElementById("slider").addEventListener("mouseleave",start);
    start();

    /* count-up */
    var nums=document.querySelectorAll("[data-count]");
    var io=new IntersectionObserver(function(es){ es.forEach(function(e){ if(!e.isIntersecting) return; var el=e.target, tg=parseInt(el.getAttribute("data-count"),10)||0, sf=el.getAttribute("data-suffix")||"", st=null;
        if(reduce){ el.textContent=tg+sf; io.unobserve(el); return; }
        function tick(ts){ if(!st)st=ts; var p=Math.min((ts-st)/1500,1), v=Math.round(tg*(1-Math.pow(1-p,3))); el.textContent=v+sf; if(p<1)requestAnimationFrame(tick); else el.textContent=tg+sf; }
        requestAnimationFrame(tick); io.unobserve(el);
    }); },{threshold:.5});
    nums.forEach(function(el){ io.observe(el); });
})();
