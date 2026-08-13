/* ==========================================================
                    EARN CASH PLATFORM
                    MAIN JAVASCRIPT
========================================================== */





/* ==========================================================
                    CURSOR GLOW EFFECT
========================================================== */


const cursorGlow = document.querySelector(".cursor-glow");



if(cursorGlow){


document.addEventListener("mousemove",(event)=>{


cursorGlow.style.left =

event.clientX + "px";



cursorGlow.style.top =

event.clientY + "px";



});


}








/* ==========================================================
                    MOBILE MENU
========================================================== */


const menuBtn =

document.querySelector(".menu-btn");



const navLinks =

document.querySelector(".nav-links");





if(menuBtn){



menuBtn.addEventListener("click",()=>{


navLinks.classList.toggle("active");


});



}







/* ==========================================================
                    NAVBAR SCROLL EFFECT
========================================================== */


const navbar =

document.querySelector(".navbar");





window.addEventListener("scroll",()=>{


if(window.scrollY > 50){


navbar.classList.add("scrolled");


}

else{


navbar.classList.remove("scrolled");


}



});
/* ==========================================================
                    SCROLL REVEAL SYSTEM
========================================================== */


const revealElements =

document.querySelectorAll(".reveal");



const revealObserver =

new IntersectionObserver((entries)=>{


entries.forEach(entry=>{


if(entry.isIntersecting){


entry.target.classList.add("active");


}


});


},


{


threshold:.15


});





revealElements.forEach(element=>{


revealObserver.observe(element);


});









/* ==========================================================
                    DASHBOARD 3D MOVEMENT
========================================================== */


const dashboard =

document.querySelector(".dashboard-wrapper");





if(dashboard){



document.addEventListener("mousemove",(event)=>{



const rotateY =

(event.clientX - window.innerWidth / 2) / 60;



const rotateX =

(window.innerHeight / 2 - event.clientY) / 60;





dashboard.style.transform =


`
rotateY(${rotateY}deg)

rotateX(${rotateX}deg)
`;



});






dashboard.addEventListener("mouseleave",()=>{


dashboard.style.transform =

"rotateY(0deg) rotateX(0deg)";



});



}








/* ==========================================================
                    REFERRAL CTA (marketing preview)
   The hero "Referral Dashboard" widget is an illustrative
   example shown to signed-out visitors — there is no real
   referral link to copy until someone actually registers, so
   this element is a plain link to the registration page
   (see pages/index.html) rather than a fake clipboard action.
========================================================== */
/* ==========================================================
                    SMOOTH SCROLLING
========================================================== */


document.querySelectorAll('a[href^="#"]').forEach(link=>{


link.addEventListener("click",function(event){



const target =

document.querySelector(

this.getAttribute("href")

);



if(target){



event.preventDefault();



target.scrollIntoView({


behavior:"smooth"



});



}



});



});









/* ==========================================================
                    CURRENT YEAR
========================================================== */


const year =

document.querySelector(".current-year");



if(year){


year.textContent =

new Date().getFullYear();



}









/* ==========================================================
                    BUTTON RIPPLE EFFECT
========================================================== */


const buttons =

document.querySelectorAll(".btn");





buttons.forEach(button=>{



button.addEventListener("click",function(event){



const ripple =

document.createElement("span");



const rect =

this.getBoundingClientRect();





ripple.style.left =

event.clientX - rect.left + "px";





ripple.style.top =

event.clientY - rect.top + "px";





ripple.classList.add("ripple");



this.appendChild(ripple);





setTimeout(()=>{


ripple.remove();



},600);



});



});









/* ==========================================================
                    PAGE LOAD EFFECT
========================================================== */


window.addEventListener("load",()=>{


document.body.classList.add("loaded");



});







/* ==========================================================
                    DISABLE HEAVY EFFECTS
                    WHEN TAB HIDDEN
========================================================== */


document.addEventListener(

"visibilitychange",

()=>{



if(document.hidden){



document.body.classList.add(

"pause-animation"

);



}

else{



document.body.classList.remove(

"pause-animation"

);



}



});
