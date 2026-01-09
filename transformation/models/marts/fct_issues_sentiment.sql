with staging as (
    -- get the cleaned and typed staging data
    select * from {{ ref('stg_github_issues') }}
),

enriched as (
    select
        issue_id,
        repo_name,
        created_at,
        title,
        body, -- keep body for sentiment analysis
        
        -- CORTEX AI Sentiment Analysis
        -- function: SNOWFLAKE.CORTEX.SENTIMENT(texto)
        -- concat title and body to get overall sentiment
        SNOWFLAKE.CORTEX.SENTIMENT(concat(title, ' ', body)) as sentiment_score,
        
        -- KPIs
        hours_to_close

    from staging
    -- quality filter
    -- if no body or too short, skip
    where body is not null and len(body) > 10
),

final as (
    select
        *,

        -- conveert sentiment score to label
        case 
            when sentiment_score < -0.1 then 'Negative'  
            when sentiment_score > 0.1 then 'Positive'  
            else 'Neutral'
        end as sentiment_label
    from enriched
)

select * from final