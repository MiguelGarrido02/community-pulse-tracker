with source as (
    -- Refer to the raw source table
    select * from {{ source('github_source', 'github_issues') }}
),


renamed as (
    select
        issue_id,
        repo_name,
        ingested_at,
        
        
        -- FORCE SNOWFLAKE TO INTERPRET AS JSON this took me too long to figure out
        PARSE_JSON(payload) as json_content
        
    from source
    where payload is not null
),

parsed as (
    select
        issue_id,
        repo_name,
        ingested_at,

        -- Extraction and Cast (Type Conversion)
        -- Snowflake allows navigating JSON with ":"
        json_content:number::int as issue_number,
        json_content:title::varchar as title,
        json_content:state::varchar as state,

        -- Handling timestamps
        json_content:created_at::timestamp as created_at,
        json_content:updated_at::timestamp as updated_at,
        json_content:closed_at::timestamp as closed_at,

        -- User data (nested in JSON)
        json_content:user.login::varchar as user_login,
        json_content:user.type::varchar as user_type,
        -- Text cleaning (if body is null, put empty string)
        coalesce(json_content:body::varchar, '') as body,

        -- URL for linking from the dashboard
        json_content:html_url::varchar as url,

        -- difference in hours between created_at and closed_at
        datediff('hour', json_content:created_at::timestamp, json_content:closed_at::timestamp) as hours_to_close

    from renamed
)

select * from parsed