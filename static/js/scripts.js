function generate_chart(
    json_data,
    data_x_name, 
    data_y_name, 
    bindto_id)
{

  var chart = c3.generate({
    bindto: '#'+bindto_id,
    data: {
      x: 'x',
      xFormat: '%Y/%d/%m %H:%M:%S',
      json: json_data,
      keys: {
        x: data_x_name, // it's possible to specify 'x' when category axis
        value: [data_y_name]
      }
    },
    axis: {
        x: {
            type: 'timeseries',
            tick: {
                format: '%Y/%d/%m %H:%M:%S'
            }
        }
    },
    legend: {
        position: 'bottom'
    },
    zoom: {
        enabled: true
    }
  });

  return chart;
}

jQuery(document).ready(function(){

  jQuery('.copy').click(function(){
      let tmp = jQuery('<textarea>');
      jQuery("body").append(tmp);
      tmp.val(jQuery(this).attr('data-copy')).select();
      document.execCommand("copy");
      tmp.remove();
  })

  jQuery('form#charts button').click(function(){

    jQuery.getJSON($SCRIPT_ROOT + '/_metrics', {
          interval: jQuery('input[name="interval"]:checked').val(),
          metric_name: jQuery('input[name="metric_name"]:checked').val(),
          mode: 'live',
        }, function(data) {
          console.log(data);
          generate_chart(data.json_data, data.x_name, data.y_name, 'chart');
        });
    });
})

