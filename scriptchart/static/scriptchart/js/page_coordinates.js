(function($) {
  function annotator() {
    $("#annotator").html('');
    new BBoxAnnotator({
      id: "annotator",
      url: $("#id_url").val(),
      scale: 1 / (2 ** -parseFloat($("#zoom").val())),
      input_method: "select",  // ['text', 'select', 'fixed']
      datalist: "letters", // only needed if text
      labels: $.map($("#letters").children(), option => $(option).val()), // only needed if select
      entries: JSON.parse($("#id_annotations").val() || "[]"),
      onchange: function(entries) {
        $("#id_annotations").val(JSON.stringify(entries))
      }
    });
    $("input[type=checkbox]").each(function() {
      const checkbox = $(".annotated_bounding_box:contains("+ this.name +")");
      if (this.checked) {
        checkbox.show();
      } else {
        checkbox.hide();
      }
    });
  }

  $(document).ready(function() {
    // Annotator and zoom controls
    $("#zoom").on("input", annotator);
    $("#zoom").trigger("input");
    $("#method").on("change", annotator);
    // Letters
    $("input[type=checkbox]").on("change", function(event) {
      const checkbox = $(".annotated_bounding_box:contains("+ event.target.name +")");
      if (event.target.checked) {
        checkbox.show();
      } else {
        checkbox.hide();
      }
    });
    $("button#letters-all").on("click", function(event) {
      $(".annotated_bounding_box").show();
      $(".letter-toggles").prop("checked", true);
      event.preventDefault();
    });
    $("button#letters-none").on("click", function(event) {
      $(".annotated_bounding_box").hide();
      $(".letter-toggles").prop("checked", false);
      event.preventDefault();
    });
  });
})(jQuery);
