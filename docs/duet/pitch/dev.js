/* Developer mode (press D): hover shows an element's data-el name, click copies it.
   From ~/.claude/rules/common/preview-dev-mode.md. */
(function(){
  var label=document.getElementById('devLabel'),toast=document.getElementById('devToast'),tT=null;
  function isDev(){return document.body.classList.contains('dev');}
  function copy(t){if(navigator.clipboard&&navigator.clipboard.writeText){navigator.clipboard.writeText(t)['catch'](fb);}else fb();
    function fb(){var a=document.createElement('textarea');a.value=t;a.style.position='fixed';a.style.opacity='0';document.body.appendChild(a);a.select();try{document.execCommand('copy');}catch(e){}document.body.removeChild(a);}}
  function toastMsg(m){toast.textContent=m;toast.classList.add('show');if(tT)clearTimeout(tT);tT=setTimeout(function(){toast.classList.remove('show');},1400);}
  document.addEventListener('keydown',function(e){var t=e.target;if(t&&t.matches&&t.matches('input,textarea,[contenteditable]'))return;
    if(e.key==='d'||e.key==='D'){document.body.classList.toggle('dev');if(!isDev())label.style.display='none';}});
  document.addEventListener('mousemove',function(e){if(!isDev()){label.style.display='none';return;}
    var el=e.target.closest?e.target.closest('[data-el]'):null;
    if(el){label.textContent=el.getAttribute('data-el');label.style.display='block';
      label.style.left=Math.min(e.clientX+12,window.innerWidth-label.offsetWidth-8)+'px';label.style.top=(e.clientY+14)+'px';}
    else label.style.display='none';});
  document.addEventListener('click',function(e){if(!isDev())return;
    var el=e.target.closest?e.target.closest('[data-el]'):null;if(!el)return;
    e.preventDefault();e.stopPropagation();var n=el.getAttribute('data-el');copy(n);toastMsg('Copied: '+n);},true);
})();
