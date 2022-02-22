from datetime import datetime, timedelta

import matplotlib.ticker as mtick
import pandas as pd
from matplotlib import cm, colors
from matplotlib import pyplot as plt


def compute_cumulative_returns(asset_price_df, col_name):
    """
    Computes cumulative return given price data
    @param asset_price_df: pd.DataFrame:
        pandas dataframe containing price data
    @param col_name: str
        sets pandas DataFrame column name
    @return: pd.DataFrame
        pandas dataframe of cumulative returns
    """
    cumulative_return = ((1 + asset_price_df.ffill().pct_change()).cumprod().iloc[-1] - 1) * 100
    return cumulative_return.to_frame(name=col_name)


def returns_df(asset_prices_df):
    """
    Computes cumulative returns across sectors
    @param asset_prices_df: pd.DataFrame
        pandas dataframe of asset prices
    @return: pd.DataFrame
        pandas dataframe with asset returns
    """
    end = asset_prices_df.index[-1]
    end_date = end.strftime('%Y-%m-%d')

    # Compute returns over specified period
    seven_day = (end - timedelta(7)).strftime('%Y-%m-%d')
    one_month = (end - timedelta(30)).strftime('%Y-%m-%d')
    three_month = (end - timedelta(90)).strftime('%Y-%m-%d')
    six_month = (end - timedelta(180)).strftime('%Y-%m-%d')
    seven_day_return = compute_cumulative_returns(asset_prices_df.loc[seven_day:end_date],
                                                  f'7-day Return {seven_day} - {end_date}')
    one_month_return = compute_cumulative_returns(asset_prices_df.loc[one_month:end_date],
                                                  f'1-month Return {one_month} - {end_date}')
    three_month_return = compute_cumulative_returns(asset_prices_df.loc[three_month:end_date],
                                                    f'3-month Return {three_month} - {end_date}')
    six_month_return = compute_cumulative_returns(asset_prices_df.loc[six_month:end_date],
                                                  f'6-month Return {six_month} - {end_date}')
    asset_returns = pd.concat([seven_day_return, one_month_return, three_month_return, six_month_return], axis=1)
    return asset_returns


def hot_ball_of_money(asset_returns, sector_mapping):
    """
    Generated Hot Ball of Money monitor
    @param asset_returns: pd.DataFrame
        pandas dataframe with asset returns
    @param sector_mapping: dict
        Dictionary of asset:sector mapping
    @return: matplotlib fig
        figure containing Hot Ball of Money Monitor
    """
    # Construct color map from sector mapping
    sectors = list(set(sector_mapping.values()))
    cmap = cm.get_cmap('Spectral', len(sectors))
    cmap = [colors.rgb2hex(cmap(i)) for i in range(cmap.N)]
    color_mapping = {sector: color for sector, color in zip(sectors, cmap)}

    asset_returns['sector'] = asset_returns.index.map(sector_mapping)
    color_list = [color_mapping[i] for i in asset_returns['sector']]
    fig = plt.figure(figsize=(30, 15))
    handles = [plt.Rectangle((0, 0), 1, 1, color=color_mapping[sector]) for sector in sectors]
    for col, i in zip(asset_returns.columns, range(1, len(asset_returns.columns))):
        if col == 'sector':
            continue
        else:
            ax = asset_returns[col].plot(kind='bar', ax=plt.subplot(int(str('24') + str(i))), color=color_list)
            ax.set_title(col, fontsize=18)
            ax.set_ylabel('Total Return (%)')
            ax.yaxis.set_major_formatter(mtick.PercentFormatter())
            plt.suptitle('Hot Ball of Money Monitor', size=40)
            plt.figlegend(handles, sectors, loc='lower center', ncol=3, prop={'size': 16})
    average_sector_returns = asset_returns.groupby('sector').mean()
    average_sector_returns = average_sector_returns.reindex(list(asset_returns['sector'].unique()))
    average_sector_returns.index = [x.replace(' ', '\n') for x in average_sector_returns.index]
    for col, i in zip(average_sector_returns.columns, range(5, len(average_sector_returns.columns) + 5)):
        tmp_df = average_sector_returns[col].to_frame(name=col)
        tmp_df['positive'] = tmp_df[col] > 0
        best_performing_sector = tmp_df[col].sort_values().index[-1]
        tmp_df.loc[best_performing_sector, 'positive'] = 'Best'
        ax = tmp_df[col].plot(kind='bar', ax=plt.subplot(int(str('24') + str(i))), rot=0, legend=False,
                              color=tmp_df.positive.map({True: 'g', False: 'r', 'Best': '#D1B000'}))
        split_col = col.split(' ')
        ax.set_title(f'{split_col[0]} Average Sector {split_col[1]}', fontsize=18)
        ax.set_ylabel('Total Return (%)')
        ax.set_xlabel('')
        ax.yaxis.set_major_formatter(mtick.PercentFormatter())
    fig.savefig('hotballofmoney.png', dpi=300)