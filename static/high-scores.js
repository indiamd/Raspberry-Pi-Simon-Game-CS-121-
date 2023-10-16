var button = $("#play_game_button");
var message = $("#game_over");

button.click(function() {
    console.log(button.text());
   
    $.ajax({
        url: "/play_game",
        type: "post",
        success: function(response) {
            console.log(response);
            var points= response;
            button.text("Game over. You scored " + response);
        }
    });



});

