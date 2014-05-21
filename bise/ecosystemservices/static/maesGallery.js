$(document).ready(function() {
  $("#owl-example").owlCarousel({
    navigation: true,
    lazyLoad : true,
    navigationText: [
      "<i class='icon-chevron-left icon-white'></i>",
      "<i class='icon-chevron-right icon-white'></i>"
    ],
    rewindNav: false,
    items: 4
  }); 
  dojo.require("esri.arcgis.utils");
  dojo.require('esri.map');
  dojo.require("esri.dijit.Attribution");
  dojo.require("esri.dijit.Legend");
  dojo.require("esri.dijit.LocateButton");
  dojo.require("esri.dijit.Geocoder");

  var webmaps = [], map, currentMap = 0;
  var extent = null;

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
      if (extent){
        map.setExtent(extent);
      }
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
      var geoLocate = new esri.dijit.LocateButton({
        map: map
      }, dojo.create('div', 
        {id: 'locate'+id},
        dojo.byId('locateDiv')));
      geoLocate.startup();

      var geocoder = new esri.dijit.Geocoder({ 
        map: map 
      }, dojo.create('div', 
        {id: 'geocoder'+id},
        dojo.byId('geocodeDiv')));
      geocoder.startup();
      
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
      myMap.setExtent(extent)
      var node = dojo.byId(myMap.id);
      esri.show(node);
      var anim = dojo.fadeIn({
        node: node
      });
      anim.play();
      updateDetails(myMap);
      esri.show(dojo.byId("legend"+currentMap));
      esri.show(dojo.byId("locate"+currentMap));
      esri.show(dojo.byId("geocoder"+currentMap));
    }else{
      createMap(id);
    }
    
  }
  function init(){
    createMap("875f8687b559436797383a1b4ef574cb");
  }
  function hideCurrentMap(){
    var node = dojo.byId(currentMap);
    esri.hide(node);
    var anim = dojo.fadeOut({
      node: node
    });
    anim.play();
    esri.hide(dojo.byId("legend"+currentMap));
    esri.hide(dojo.byId("locate"+currentMap));
    esri.hide(dojo.byId("geocoder"+currentMap));
  }
  function updateDetails(item){
    dojo.byId("title").innerHTML = item.title;
    dojo.byId("attribution").innerHTML = item.owner;
  }
  dojo.ready(init);
});