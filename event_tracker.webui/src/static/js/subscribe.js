$(document).on('submit','#subscribe_form',function(e){
e.preventDefault();

var subscribeData = $(this).find('input[name="subscribe_data_from_form"]').val();

$.ajax({
type:'POST',
url:'/subscribe_to_event',
data:{
subscribe_data_from_js: subscribeData
},
success:function()
{
alert('вы подписались на ');
}
})
});