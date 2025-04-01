{{config(materialized = 'view')}}

with source_data as 
(
    select *, row_number() over() as rn
    from {{source('staging', 'artwork_external_table')}}
    where id is not null
)

select 
    id, 
    accession_number,
    artist,
    artistRole,
    artistId,
    title,
    dateText,
    medium,
    creditLine,
    CASE 
        WHEN year IS NULL THEN NULL
        WHEN year = -1 THEN NULL
        ELSE year 
    END as year,
    CASE 
        WHEN acquisitionYear IS NULL THEN NULL
        WHEN acquisitionYear = -1 THEN NULL
        ELSE acquisitionYear 
    END as acquisitionYear,
    CASE
        WHEN year IS NULL THEN NULL
        WHEN year = -1 THEN NULL
        WHEN acquisitionYear IS NULL THEN NULL
        WHEN acquisitionYear = -1 THEN NULL
        ELSE acquisitionYear - year 
    END as age_at_acquisition,
    dimensions,
    CASE 
        WHEN width IS NULL THEN NULL
        WHEN SAFE_CAST(width as int64) = -1 THEN NULL
        ELSE width 
    END as width,
     CASE 
        WHEN height IS NULL THEN NULL
        WHEN SAFE_CAST(height as int64) = -1 THEN NULL
        ELSE height 
    END as height,
    CASE 
        WHEN depth IS NULL THEN NULL
        WHEN SAFE_CAST(depth as int64) = -1 THEN NULL
        ELSE depth 
    END as depth,
    units,
    inscription,
    thumbnailCopyright,
    thumbnailUrl,
    url
from source_data

-- dbt build --select <model_name> --vars '{'is_test_run': 'false'}'
{% if var('is_test_run', default=true) %}

  limit 100

{% endif %}

