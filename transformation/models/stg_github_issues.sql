with source as (
    -- Refer to the raw source table
    select * from {{ source('github_source', 'github_issues') }}
),

renamed as (
    select
        issue_id,
        repo_name,
        ingested_at,

        -- Extraction and Cast (Type Conversion)
        -- Snowflake allows navigating JSON with ":"
        payload:number::int as issue_number,
        payload:title::varchar as title,
        payload:state::varchar as state,

        -- Handling timestamps
        payload:created_at::timestamp as created_at,
        payload:updated_at::timestamp as updated_at,
        payload:closed_at::timestamp as closed_at,

        -- User data (nested in JSON)
        payload:user.login::varchar as user_login,
        payload:user.type::varchar as user_type,

        -- Text cleaning (if body is null, put empty string)
        coalesce(payload:body::varchar, '') as body,

        -- URL for linking from the dashboard
        payload:html_url::varchar as url,

        -- difference in hours between created_at and closed_at
        datediff('hour', payload:created_at::timestamp, payload:closed_at::timestamp) as hours_to_close

    from source
)

select * from renamed