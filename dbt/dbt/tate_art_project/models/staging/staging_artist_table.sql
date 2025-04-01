{{config(materialized = 'view')}}

with source_data as 
(
    select *, row_number() over() as rn
    from {{source('staging', 'artist_external_table')}}
    where id is not null
)

select 
    id, 
    name,
    gender,
    dates,
    COALESCE(yearOfBirth, -1) as yearOfBirth,
    yearOfDeath,
    CASE 
        WHEN yearOfBirth IS NULL THEN NULL
        WHEN yearOfBirth = -1 THEN NULL
        WHEN yearOfDeath IS NULL THEN (EXTRACT(YEAR FROM CURRENT_DATE()) - yearOfBirth)
        ELSE (yearOfDeath - yearOfBirth)
    END AS artistAge,
    placeOfBirth,
    placeOfDeath,
    url
from source_data

-- dbt build --select <model_name> --vars '{'is_test_run': 'false'}'
{% if var('is_test_run', default=true) %}

    limit 100

{% endif %}