""" Module that contains functions and parameters common to the Google Earth Engine vegetation change detection project workflow  """

# IMPORTS
import ee

# HELPER FUNCTIONS


def mask_landsat8_sr(image):
    """Mask clouds and cloud shadows in Landsat surface reflectance image.

    Obtained from:
        https://developers.google.com/earth-engine/datasets/catalog/LANDSAT_LC08_C01_T2_SR

    """
    # Define cloud (5) and cloud shadow (3) mask bits
    cloud_shadow_bit_mask = (1 << 3)
    cloud_bit_mask = (1 << 5)

    # Get the pixel QA band
    qa = image.select('pixel_qa')

    # Mask image, based on both bit masks == 0
    mask = qa.bitwiseAnd(cloud_shadow_bit_mask).eq(
        0) and qa.bitwiseAnd(cloud_bit_mask).eq(0)

    return image.updateMask(mask)


def add_ndvi(image):
    """Calculates Landsat 8 NDVI and adds NDVI band to image."""
    ndvi = image.normalizedDifference(['B5', 'B4']).rename('NDVI')
    return image.addBands(ndvi)


def image_collection_to_list(collection):
    """Converts ImageCollection to ee.List object."""
    return collection.toList(collection.size())


def subtract_ndvi_bands(collection_as_list, post_change_index, pre_change_index):
    """Subtracts NDVI bands for two ee.Image objects."""
    post_change_ndvi = ee.Image(
        collection_as_list.get(post_change_index)).select('NDVI')

    pre_change_ndvi = ee.Image(
        collection_as_list.get(pre_change_index)).select('NDVI')

    return post_change_ndvi.subtract(pre_change_ndvi)

# MAIN FUNCTIONS


def ndvi_diff_landsat8(image_collection, post_change_index, pre_change_index):
    """Creates NDVI difference (Landsat 8) between two
    ee.Image objects in an ee.ImageCollection object."""
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

    Function for OBIA - takes one-band NDVI difference image
    and segments/classifies with OBIA (SNIC) based on NDVI
    thresholds.
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
vis_params_rgb = {
    'bands': ['B4', 'B3', 'B2'],
    'min': 0,
    'max': 2500
}

vis_params_cir = {
    'bands': ['B5', 'B4', 'B3'],
    'min': 0,
    'max': 2500
}

vis_params_ndvi = {
    'min': -1,
    'max': 1,
    'palette': ['red', '#ece6d6', 'green']
}

vis_params_ndvi_diff = {
    'min': -2,
    'max': 2,
    'palette': ['red', '#ece6d6', 'green']
}

vis_params_ndvi_sld = \
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
