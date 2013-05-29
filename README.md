samstemmer
==========

Prosjekt for å automatisere innsamling og metode i analyser av stortingsdata

### Bibliotek
- django
- jquery
- d3
- rpy
- r (?)
* http://tablesorter.com/docs/#Examples
* http://plugins.learningjquery.com/expander/index.html#getting-started



### ideer til videreutvikling:


- [denne](https://docs.google.com/spreadsheet/ccc?key=0AgAXDJuvjySMdDlVOWJIclRRTkhPTmxIRjVRU01jMEE):  beviser at [denne](http://www.nrk.no/valg2013/_-regjeringen-tommer-skuffene-1.11038459) er vinklet helt mot det dataene sier, og at det enten er feil i spørringen min* eller så tabber intervjuobjektene seg ut på overdreven negativ omtale av den vanlige tralten på Tinget på for-sommer'n.

* 
> SELECT *, count(*) AS "antall saker" FROM fylkesperspektiv_saker GROUP BY YEAR(sist_oppdatert_dato), MONTH(sist_oppdatert_dato);



## Ubehagelige saker utsettes til rett før en ferie?
> SELECT *, CONCAT(YEAR(votering_tid), ' ', MONTHNAME(votering_tid)) as tid, count(*) as antall FROM `fylkesperspektiv_votering` GROUP BY YEAR(`votering_tid`), MONTH(`votering_tid`);

Desember og juni er topp-måneder, [google docs graf](https://docs.google.com/spreadsheet/ccc?key=0AgAXDJuvjySMdDlVOWJIclRRTkhPTmxIRjVRU01jMEE&usp=sharing) så ja, kanskje? Hvordan kan vi finne ut om disse toppene inneholder ubehageligheter for koalisjonene?








## innmeldte bugs:
- "se mer" javascript-knappene f.eks. på personer med mange spørsmål lukker seg selv etter egen vilje. 



- [x] @mentions, #refs, [links](), **formatting**, and <del>tags</del> supported
- [x] list syntax required (any unordered or ordered list supported)
- [x] this is a complete item
- [ ] this is an incomplete item



# H1
## H2
### H3
#### H4
##### H5
###### H6





Emphasis, aka italics, with *asterisks* or _underscores_.

Strong emphasis, aka bold, with **asterisks** or __underscores__.

Combined emphasis with **asterisks and _underscores_**.

Strikethrough uses two tildes. ~~Scratch this.~~

[I'm an inline-style link](https://www.google.com)

[I'm a reference-style link][Arbitrary case-insensitive reference text]

[You can use numbers for reference-style link definitions][1]

Or leave it empty and use the [link text itself][]

Some text to show that the reference links can follow later.

[arbitrary case-insensitive reference text]: https://www.mozilla.org
[1]: http://slashdot.org
[link text itself]: http://www.reddit.com


Inline-style: 
![alt text](https://github.com/adam-p/markdown-here/raw/master/src/common/images/icon48.png "Logo Title Text 1")

Reference-style: 
![alt text][logo]

[logo]: https://github.com/adam-p/markdown-here/raw/master/src/common/images/icon48.png "Logo Title Text 2"

....

Inline `code` has `back-ticks around` it.


 ```javascript
 var s = "JavaScript syntax highlighting";
 alert(s);
 ```
 
 ```python
 s = "Python syntax highlighting"
 print s
 ```
 
 ```
 No language indicated, so no syntax highlighting. 
 But let's throw in a <b>tag</b>.
 ```

 > Sitat?

<dl>
  <dt>Definition list</dt>
  <dd>Is something people use sometimes.</dd>

  <dt>Markdown in HTML</dt>
  <dd>Does *not* work **very** well. Use HTML <em>tags</em>.</dd>
</dl>

....

<a href="http://www.youtube.com/watch?feature=player_embedded&v=YOUTUBE_VIDEO_ID_HERE
" target="_blank"><img src="http://img.youtube.com/vi/YOUTUBE_VIDEO_ID_HERE/0.jpg" 
alt="IMAGE ALT TEXT HERE" width="240" height="180" border="10" /></a>