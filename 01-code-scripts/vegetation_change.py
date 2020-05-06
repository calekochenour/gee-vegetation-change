""" Module that contains functions and parameters common to the Google Earth Engine vegetation change detection project workflow  """

# IMPORTS
import ee

# HELPER FUNCTIONS


def mask_landsat8_sr(image):
    """Mask clouds and cloud shadows in Landsat surface reflectance image.

    Obtained from:
        https://developers.google.com/earth-engine/datasets/catalog/LANDSAT_LC08_C01_T2_SR

    Parameters
    ----------
    image : ee.Image
        Input image (Landsat 8 Surface Reflectance).

    Returns
    -------
    N/A : ee.Image
        Input image masked for clouds and cloud shadows.

    Example
    -------
        >>> import ee
        >>> peak_green = ee.Image('LANDSAT/LC08/C01/T1_SR/LC08_008057_20170602'
        >>> peak_green_mask = mask_landsat8_sr(peak_green)
    """
    # Define cloud (5) and cloud shadow (3) mask bits
    cloud_shadow_bit_mask = (1 << 3)
    cloud_bit_mask = (1 << 5)

    # Get the pixel QA band
    qa = image.select('pixel_qa')

    # Mask image, based on both bit masks == 0
    mask = qa.bitwiseAnd(cloud_shadow_bit_mask).eq(
        0) and qa.bitwiseAnd(cloud_bit_mask).eq(0)

    # Return masked image
    return image.updateMask(mask)


def add_ndvi(image):
    """Calculates Landsat 8 NDVI and adds NDVI band to image.

    Parameters
    ----------
    image : ee.Image
        Input image (Landsat 8).

    Returns
    -------
    N/A : ee.Image
        Input image with NDVI band added to list of bands.

    Example
    -------
        >>> import ee
        >>> peak_green = ee.Image('LANDSAT/LC08/C01/T1_SR/LC08_008057_20170602'
        >>> peak_green_ndvi = add_ndvi(peak_green)
        >>> ndvi_band = peak_green.select('NDVI')
    """
    # Calculate NDVI
    ndvi = image.normalizedDifference(['B5', 'B4']).rename('NDVI')

    # Return image with NDVI band
    return image.addBands(ndvi)


def image_collection_to_list(collection):
    """Converts ee.ImageCollection to ee.List object.

    Parameters
    ----------
    collection : ee.ImageCollection
        Collection of ee.Image objects.

    Returns
    -------
    N/A : ee.List
        Input ee.ImageCollection as type ee.List.

    Example
    -------
        >>> import ee
        >>> peak_green = ee.Image('LANDSAT/LC08/C01/T1_SR/LC08_008057_20170602')
        >>> post_harvest = ee.Image('LANDSAT/LC08/C01/T1_SR/LC08_008057_20170906')
        >>> image_collection = ee.ImageCollection([peak_green, post_harvest])
        >>> image_list = image_collection_to_list(image_collection)
    """
    # Return collection as ee.List object
    return collection.toList(collection.size())


def subtract_ndvi_bands(collection_as_list, post_change_index, pre_change_index):
    """Subtracts NDVI bands for two ee.Image objects.

    Parameters
    ----------
    collection_as_list : ee.List
        Collection of ee.Image objects as type ee.List.

    post_change_index : int
        List index for the post-change image.

    pre_change_index : int
        List index for the pre-change image.

    Returns
    -------
    N/A : ee.Image
        Single-band image of the NDVI difference.

    Example
    -------
        >>> import ee
        >>> peak_green = ee.Image('LANDSAT/LC08/C01/T1_SR/LC08_008057_20170602')
        >>> post_harvest = ee.Image('LANDSAT/LC08/C01/T1_SR/LC08_008057_20170906')
        >>> image_collection = ee.ImageCollection([peak_green, post_harvest])
        >>> image_list = image_collection_to_list(image_collection)
        >>> ndvi_diff = subtract_ndvi_bands(image_list, 1, 0)
    """
    # Get post-change image NDVI band
    post_change_ndvi = ee.Image(
        collection_as_list.get(post_change_index)).select('NDVI')

    # Get pre-change image NDVI band
    pre_change_ndvi = ee.Image(
        collection_as_list.get(pre_change_index)).select('NDVI')

    # Return NDVI difference (post-change - pre-change)
    return post_change_ndvi.subtract(pre_change_ndvi)

# MAIN FUNCTIONS


def ndvi_diff_landsat8(image_collection, post_change_index, pre_change_index):
    """Creates NDVI difference (Landsat 8) between two
    ee.Image objects in an ee.ImageCollection object.

    Uses four helper functions:
        mask_landsat8_sr()
        add_ndvi()
        image_collection_to_list()
        subtract_ndvi_bands()

    Parameters
    ----------
    image_collection : ee.ImageCollection
        Collection of ee.Image objects.

    post_change_index : int
        List index for the post-change image.

    pre_change_index : int
        List index for the pre-change image.

    Returns
    -------
    ndvi_diff : ee.Image
        Single-band image of the NDVI difference.

    Example
    -------
        >>> import ee
        >>> peak_green = ee.Image('LANDSAT/LC08/C01/T1_SR/LC08_008057_20170602')
        >>> post_harvest = ee.Image('LANDSAT/LC08/C01/T1_SR/LC08_008057_20170906')
        >>> image_collection = ee.ImageCollection([peak_green, post_harvest])
        >>> ndvi_diff = ndvi_diff_landsat8(image_collection, 1, 0)
    """
    # EXECUTE HELPER FUNCTIONS
    # Mask clouds and cloud shadows for each image in the collection
    collection_masked = image_collection.map(mask_landsat8_sr)

    # Add NDVI band to each image in the collection
    collection_ndvi = collection_masked.map(add_ndvi)

    # Convert ImageCollection into list
    collection_list = image_collection_to_list(collection_ndvi)

    # Compute NDVI difference for specified image indices in the collection
    ndvi_diff = subtract_ndvi_bands(
        collection_list, post_change_index, pre_change_index)

    # Return NDVI difference
    return ndvi_diff


def segment_snic(ndvi_diff_image, study_area_bound, threshold_vals):
    """Segments and classifies an image based on NDVI thresholds.

    Function for segmentation - takes one-band NDVI difference
    image and segments/classifies with (SNIC) based on NDVI thresholds.

    Parameters
    ----------
    ndvi_diff_image : ee.Image
        Single-band image of the NDVI difference between two images.

    study_area_bound : ee.FeatureCollection
        Study area boundary.

    threshold_vals : list
        NDVI thresholds for classification (length == 4). Order
        of values is [primary min, primary max, secondary min,
        secondary max].

    Returns
    -------
    change : dictionary
        Dictionary containing two classes of change, based on
        threshold values. Keys are 'primary' and 'secondary'.

    Example
    -------
        >>> import ee
        >>> peak_green = ee.Image('LANDSAT/LC08/C01/T1_SR/LC08_008057_20170602')
        >>> post_harvest = ee.Image('LANDSAT/LC08/C01/T1_SR/LC08_008057_20170906')
        >>> image_collection = ee.ImageCollection([peak_green, post_harvest])
        >>> ndvi_diff = ndvi_diff_landsat8(image_collection, 1, 0)
        >>> study_area_boundary = ee.FeatureCollection("users/calekochenour/vegetation-change/drtt_study_area_boundary")
        >>> ndvi_change_thresholds = [-2.0, -0.5, -0.5, -0.35]
        >>> change_features = segment_snic(ndvi_diff, study_area_boundary, ndvi_change_thresholds)
        >>> change_primary_raster = change_features.get('primary')
        >>> change_secondary_raster = change_features.get('secondary')
    """
    # Create seed points within study area boundary
    seeds = ee.Algorithms.Image.Segmentation.seedGrid(
        24).clip(study_area_bound)

    # Segment based on SNIC (Simple Non-Iterative Clustering)
    snic = ee.Algorithms.Image.Segmentation.SNIC(**{
        'image': ndvi_diff_image,
        'size': 36,
        'compactness': 5,
        'connectivity': 8,
        'neighborhoodSize': 256,
        'seeds': seeds}).select(['NDVI_mean', 'clusters'], ['NDVI', 'clusters'])

    # Select the clusters
    clusters = snic.select('clusters')

    # Add clusters to the NDVI image
    ndvi_diff_image = ndvi_diff_image.addBands(clusters)

    # Compute per-cluster means
    clusters_mean_reduce = ndvi_diff_image.reduceConnectedComponents(
        ee.Reducer.mean(), 'clusters', 256)

    # Define categories based on thresholds
    change_primary = (clusters_mean_reduce.select("NDVI").gte(
        threshold_vals[0])).And(clusters_mean_reduce.select("NDVI").lt(threshold_vals[1]))

    change_secondary = (clusters_mean_reduce.select("NDVI").gte(
        threshold_vals[2])).And(clusters_mean_reduce.select("NDVI").lt(threshold_vals[3]))

    # Mask non-change (outside defined thresholds) clusters
    change_primary = change_primary.updateMask(change_primary)
    change_secondary = change_secondary.updateMask(change_secondary)

    # Store change classes (primary and secondary)
    change = {
        "primary": change_primary,
        "secondary": change_secondary
    }

    return change


def raster_to_vector(objects_raster, study_area_bound):
    """Converts classified raster clusters/objects/segments
    to vectors.

    Parameters
    ----------
    objects_raster : ee.Image
        Image containing the classifed raster segments/clusters.

    study_area_bound : ee.FeatureCollection
        Study area boundary.

    Returns
    -------
    objects_vector : ee.FeatureCollection
        Classified vector segments/clusters.

    Example
    -------
        >>> import ee
        >>> peak_green = ee.Image('LANDSAT/LC08/C01/T1_SR/LC08_008057_20170602')
        >>> post_harvest = ee.Image('LANDSAT/LC08/C01/T1_SR/LC08_008057_20170906')
        >>> image_collection = ee.ImageCollection([peak_green, post_harvest])
        >>> ndvi_diff = ndvi_diff_landsat8(image_collection, 1, 0)
        >>> study_area_boundary = ee.FeatureCollection("users/calekochenour/vegetation-change/drtt_study_area_boundary")
        >>> ndvi_change_thresholds = [-2.0, -0.5, -0.5, -0.35]
        >>> change_features = segment_snic(ndvi_diff, study_area_boundary, ndvi_change_thresholds)
        >>> change_primary_vector = raster_to_vector(change_features.get('primary'), study_area_boundary)
        >>> change_secondary_vector = raster_to_vector(change_features.get('secondary'), study_area_boundary)
    """
    # Convert raster to vector
    objects_vector = objects_raster.reduceToVectors(**{
        'geometry': study_area_bound,
        'maxPixels': 20000000,
        'scale': 5
    })

    # Return vector
    return objects_vector


def export_vector(vector, description, output_name, output_method='asset'):
    """Exports vector to GEE Asset in GEE or to shapefile
    in Google Drive.

    Parameters
    ----------
    vector : ee.FeatureCollection
        Classified vector segments/clusters.

    description : str
        Description of the exported layer.

    output_name : str
        Path for the output file. Path must exist within
        Google Earth Engine Assets path or Google Drive.

    output_method : str
        Export method/destination. Options include 'asset' for
        export to Google Earth Engine Assets or 'drive' for
        export to Google Drive.

    Returns
    -------
    output_message : str
        Message indicating location of the exported layer.

    Example
    -------
        >>> import ee
        >>> peak_green = ee.Image('LANDSAT/LC08/C01/T1_SR/LC08_008057_20170602')
        >>> post_harvest = ee.Image('LANDSAT/LC08/C01/T1_SR/LC08_008057_20170906')
        >>> image_collection = ee.ImageCollection([peak_green, post_harvest])
        >>> ndvi_diff = ndvi_diff_landsat8(image_collection, 1, 0)
        >>> study_area_boundary = ee.FeatureCollection("users/calekochenour/vegetation-change/drtt_study_area_boundary")
        >>> ndvi_change_thresholds = [-2.0, -0.5, -0.5, -0.35]
        >>> change_features = segment_snic(ndvi_diff, study_area_boundary, ndvi_change_thresholds)
        >>> change_primary_vector = raster_to_vector(change_features.get('primary'), study_area_boundary)
        >>> change_secondary_vector = raster_to_vector(change_features.get('secondary'), study_area_boundary)
        >>> change_primary_export = export_vector(vector=change_primary_vector, description='Primary Change', output_name=change_primary_asset_name, output_method='asset'
        >>> change_secondary_export = export_vector(vector=change_secondary_vector, description='Secondary Change', output_name=change_secondary_asset_name, output_method='asset')
    """
    # Create export task for Google Drive
    if output_method.lower() == "drive":
        # Export vectors as shapefile to Google Drive
        task = ee.batch.Export.table.toDrive(**{
            'collection': vector,
            'description': output_name,
            'fileFormat': 'SHP'})

        # Assign output message
        output_message = f"Exporting {output_name.split('/')[-1]} to Google Drive..."

    # Create task for GEE Asset
    elif output_method.lower() == "asset":
        # Export vectors to GEE Asset
        task = ee.batch.Export.table.toAsset(**{
            'collection': vector,
            'description': description,
            'assetId': output_name})

        # Assign output message
        output_message = f"Exporting {output_name.split('/')[-1]} to GEE Asset..."

    else:
        # Rasie error
        raise ValueError("Invalid export method. Please specify 'Drive' or 'Asset'.")

    # Start export task
    task.start()

    # Return output message
    return print(output_message)


# VISUALIZATION PARAMETERS
# Landsat 8 red/green/blue (RGB)
vis_params_rgb = {
    'bands': ['B4', 'B3', 'B2'],
    'min': 0,
    'max': 2500
}

# Landsat 8 nir/red/green (CIR)
vis_params_cir = {
    'bands': ['B5', 'B4', 'B3'],
    'min': 0,
    'max': 2500
}

# NDVI
vis_params_ndvi = {
    'min': -1,
    'max': 1,
    'palette': ['red', '#ece6d6', 'green']
}

# NDVI difference
vis_params_ndvi_diff = {
    'min': -2,
    'max': 2,
    'palette': ['red', '#ece6d6', 'green']
}

# NDVI Styled Layer Descriptor
vis_params_ndvi_diff_sld = \
    '<RasterSymbolizer>' + \
    '<ColorMap type="interval" extended="false" >' + \
    '<ColorMapEntry color="#d7191c" quantity="-2" label="0"/>' + \
    '<ColorMapEntry color="#fdae61" quantity="-0.5" label="0"/>' + \
    '<ColorMapEntry color="#ece6d6" quantity="-0.25" label="0"/>' + \
    '<ColorMapEntry color="#ece6d6" quantity="0.25" label="0" />' + \
    '<ColorMapEntry color="#a6d96a" quantity="0.5" label="0"/>' + \
    '<ColorMapEntry color="#1a9641" quantity="2" label="0" />' + \
    '</ColorMap>' + \
    '</RasterSymbolizer>'

if __name__ == '__main__':
    # Import packages
    import ee

    # Initialze GEE Python API; authenticate if necessary
    try:
        ee.Initialize()

    except Exception as error:
        ee.Authenticate()
        ee.Initialize()
