def dark_plotly_style(fig):
    fig.update_layout(
        # autosize=True,          # fills the container div
        showlegend=True,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        hoverlabel=dict(
            bgcolor='rgba(30,30,30,0.9)',
            font=dict(color='white'),
            bordercolor='rgba(128,128,128,0.5)'
        )
    )
    axis_style = dict(
        showgrid=True,
        gridwidth=1,
        gridcolor='rgba(128,128,128,0.2)',
        zeroline=True,
        zerolinewidth=1,
        zerolinecolor='rgba(128,128,128,0.5)'
    )
    fig.update_xaxes(**axis_style)
    fig.update_yaxes(**axis_style)
    return fig