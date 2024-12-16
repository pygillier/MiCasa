/** Sortable lists */
htmx.onLoad(()=> {
    console.log("Sortable init")
    els = document.getElementsByClassName('sortable')
    Sortable.create(els[0],{
        handle: ".drag-handle",
        onEnd: function (evt) {
            this.option("disabled", true);
          }
    })
    console.log("Sortable end")
})
