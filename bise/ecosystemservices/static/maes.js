$(document).ready(function() {
  dojo.require("esri.arcgis.utils");
  dojo.require('esri.map');
  dojo.require("esri.dijit.Attribution");
  dojo.require("esri.dijit.Legend");

  var webmaps = [], map, currentMap = 0;

  function createMap(id){
    var mapDeferred = esri.arcgis.utils.createMap(id, 
      dojo.create('div', 
        {id: id},
        dojo.byId('mainMap')),
        {mapOptions: {
          showAttribution: true,
          slider: true
        }
    });
    mapDeferred.then(function (response) {
      map = response.map;
      map.id = response.itemInfo.item.id;
      map.title = response.itemInfo.item.title;
      map.owner = response.itemInfo.item.accessInformation;
      map.snippet = response.itemInfo.item.snippet;
      webmaps[map.id] = map;
      currentMap = map.id;
      updateDetails(map);
      var legend = esri.arcgis.utils.getLegendLayers(response);
      var legendDijit = new esri.dijit.Legend({
          map:map,
          layerInfos: legend
      }, dojo.create('div', 
        {id: 'legend'+id},
        dojo.byId('legendContainer')));

      legendDijit.startup();

      
    }, function(error){
      alert("error");
      if (map) {
        map.destroy();
        dojo.destroy(map.container);
      }
    })
  };
  function showMap(id){
    hideCurrentMap();
    currentMap = id;
    var myMap = webmaps[id];
    if (myMap && myMap.id){
      var node = dojo.byId(myMap.id);
      esri.show(node);
      var anim = dojo.fadeIn({
        node: node
      });
      anim.play();
      updateDetails(myMap);
      esri.show(dojo.byId("legend"+currentMap));
    }else{
      createMap(id);
    }
    
  }
  function init(){
    createMap("49b66cfb3b8f48dbb62e72d76f479c60");
    $(document).on('change', '#ecosystemSelector', onEcosystemChange);
    $(document).on('change', '#serviceSelector', onServiceChange);

    /**var select = dijit.byId('ecosystemSelector');

    select.on('change', function(evt) {
        alert('myselect_event');
    });*/
  }
  function hideCurrentMap(){
    var node = dojo.byId(currentMap);
    esri.hide(node);
    var anim = dojo.fadeOut({
      node: node
    });
    anim.play();
    esri.hide(dojo.byId("legend"+currentMap));
  }
  function updateDetails(item){
    dojo.byId("title").innerHTML = item.title;
    dojo.byId("attribution").innerHTML = item.owner;
  }
  dojo.ready(init);
  function onEcosystemChange(event){
    var webmapId = $(this).find(':selected').data('webmap');
    showMap(webmapId);
    $("#serviceSelector").val("empty");
  }
  function onServiceChange(event){
    var webmapId = $(this).find(':selected').data('webmap');
    showMap(webmapId);
    $("#ecosystemSelector").val("empty");
  }  
});