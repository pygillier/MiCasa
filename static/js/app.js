const modal = new bootstrap.Modal(document.getElementById("modal"))

htmx.on("htmx:afterSwap", (e) => {
  // Response targeting #dialog => show the modal
  if (e.detail.target.id == "dialog") {
    modal.show()
  }
})

/** Sortables **/
const lists = document.getElementById("sortable")

for(const el in lists) {
  let sortable = Sortable.create(lists[el]);
}
