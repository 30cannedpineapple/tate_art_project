{{
    config(
        materialized='table'
    )
}}

with artist_data as (
    select *
    from {{ ref('staging_artist_table') }}
), 
artwork_data as (
    select *
    from {{ ref('staging_artwork_table') }}
)

select
    artwork.id as artworkId,
    accession_number,
    artwork.artist as artist,
    artistRole,
    artistId,
    title,
    dateText,
    medium,
    creditLine,
    age_at_acquisition,
    dimensions,
    width,
    height,
    depth,
    units,
    inscription,
    thumbnailCopyright,
    thumbnailUrl,
    artwork.url as artworkUrl,
    name as artistName,
    gender,
    dates as artistDates,
    yearOfBirth,
    yearOfDeath,
    artistAge,
    placeOfBirth,
    placeOfDeath,
    artist.url as artistUrl
from artwork_data artwork
left join artist_data artist
on artwork.artistId = artist.id

