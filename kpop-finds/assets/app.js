
const artist=document.querySelector('#artist'),type=document.querySelector('#type'),button=document.querySelector('#find'),results=document.querySelector('#results');
const names={bts:'BTS',blackpink:'BLACKPINK','kpop-demon-hunters':'KPop Demon Hunters','stray-kids':'Stray Kids',katseye:'KATSEYE',enhypen:'ENHYPEN',aespa:'aespa',twice:'TWICE'};
const typeTerms={album:['album vinyl','collector edition album','CD photobook'],light:['light stick concert','fanlight accessories','concert merch'],wear:['tour shirt hoodie','official merch apparel','fan t-shirt'],small:['keychain charm','photocard holder','small gift'],collect:['plush collectible','figure doll','collector merch']};
function search(q){return 'https://www.amazon.com/s?k='+encodeURIComponent(q)+'&tag=unicornmagic2-20'}
function render(){const n=names[artist.value],terms=typeTerms[type.value];results.innerHTML='<strong>'+n+' — three starting points</strong>'+terms.map((t,i)=>'<a target="_blank" rel="sponsored nofollow noopener noreferrer" href="'+search(n+' '+t)+'">'+(i+1)+'. '+n+' '+t+' ↗</a>').join('')+'<p class="small">Paid links. Check the seller, exact version and whether the listing claims official licensing before purchase.</p>'}
button.addEventListener('click',render);render();
