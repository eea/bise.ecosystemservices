$(document).ready(function() {
  dojo.require("esri.arcgis.utils");
  dojo.require('esri.map');
  dojo.require("esri.dijit.Attribution");
  dojo.require("esri.dijit.Legend");
  dojo.require("esri.dijit.LocateButton");
  dojo.require("esri.dijit.Geocoder");
  dojo.require("esri.geometry.Extent");

  var webmaps = [], map, currentMap = 0;
  var extent = null;
  var initExtent = null;

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
      if (!initExtent){
        //initExtent = map.extent;
        initExtent = new esri.geometry.Extent(map.extent.xmin, map.extent.ymin, map.extent.xmax, map.extent.ymax, map.extent.spatialReference);
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
    
      if ($("#serviceSelectorNational").is(':visible') || $("#serviceSelectorSubnational").is(':visible')){     
        if (id == "d0e8c87d45b145a9b8b6a61adc63945a"){
          $("#legend"+id+"_msg").html("&nbsp;");
        }/**else{
          if ($("#serviceSelectorNational").is(':visible')){
            window.setTimeout(function(){
              $("#legend"+id+"_msg").html("Zoom to the country to visualise the selected ecosystem service");
            }, 600);
          }else{
            window.setTimeout(function(){
              $("#legend"+id+"_msg").html("Zoom to the area to visualise the selected ecosystem service");
            }, 600);            
          }
        }  */   
      }
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
      myMap.setExtent(extent);     
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

    createMap("49b66cfb3b8f48dbb62e72d76f479c60");
    $(document).on('change', '#ecosystemSelector', onEcosystemChange);
    $(document).on('change', '#serviceSelectorEurope', onServiceChange);
    $(document).on('change', '#serviceSelectorNational', onServiceChange);
    $(document).on('change', '#serviceSelectorSubnational', onServiceChange);
    $(document).on('click', '#scale div', onScaleChange);

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
  function onEcosystemChange(event){
    var webmapId = $(this).find(':selected').data('webmap');
    //extent = map.extent;
    extent = new esri.geometry.Extent(map.extent.xmin, map.extent.ymin, map.extent.xmax, map.extent.ymax, map.extent.spatialReference); 
    showMap(webmapId);
    $("#serviceSelectorEurope").val("empty");
    $("#serviceSelectorNational").val("empty");
    $("#serviceSelectorSubnational").val("empty");
  }
  function onServiceChange(event){
    var webmapId = $(this).find(':selected').data('webmap');
    if ($("#serviceSelectorEurope").is(':visible')){
      extent = new esri.geometry.Extent(map.extent.xmin, map.extent.ymin, map.extent.xmax, map.extent.ymax, map.extent.spatialReference);
    }else{
      extent = new esri.geometry.Extent(initExtent.xmin, initExtent.ymin, initExtent.xmax, initExtent.ymax, initExtent.spatialReference);
    }   
    showMap(webmapId);
    $("#ecosystemSelector").val("empty");
  }  
  function onScaleChange(event){
    if (!$(this).hasClass("disabled")){
      $(this).parent().children().removeClass("selected");
      $(this).toggleClass("selected");
      $(".serviceSelector").hide();

      $("#ecosystemSelector").val("empty"); 
      $("#serviceSelectorEurope").val("empty");
      $("#serviceSelectorNational").val("empty");
      $("#serviceSelectorSubnational").val("empty");

      //extent = initExtent;
      extent = new esri.geometry.Extent(initExtent.xmin,initExtent.ymin,initExtent.xmax,initExtent.ymax, initExtent.spatialReference);
      

      if ($(this).data("scale") == "European"){
        $("#ecosystemSelector").children().attr("disabled", false);
        $("#serviceSelectorEurope").show();        
        showMap("49b66cfb3b8f48dbb62e72d76f479c60");
      }else if ($(this).data("scale") == "National"){
        $("#ecosystemSelector").children().attr("disabled", true);
        $("#serviceSelectorNational").show();        
        showMap("d0e8c87d45b145a9b8b6a61adc63945a");
      }else if ($(this).data("scale") == "Subnational"){
        $("#ecosystemSelector").children().attr("disabled", true);
        $("#serviceSelectorSubnational").show();        
        showMap("d0e8c87d45b145a9b8b6a61adc63945a");
      }
    }
  }
});