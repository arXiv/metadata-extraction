# from elasticsearch import Elasticsearch, helpers
# import csv
# # 读取CSV文件
# file_path = 'import2ES.csv'
#
# # Elasticsearch配置
# es = Elasticsearch("http://localhost:9200",basic_auth=('elastic', '*MtLMNdiO'))  # 修改为您的Elasticsearch实例地址
# index_name = 'education_institutions'
#
# # 读取CSV文件
# actions = []
# count = 0
#
# with open(file_path, newline='', encoding='utf-8') as csvfile:
#     reader = csv.DictReader(csvfile)
#     for row in reader:
#         count += 1
#         action = {
#             "_index": index_name,
#             "_source": {
#                 "id": row['id'],
#                 "name": row['name'],
#                 "types": row['types'],
#                 "status": row['status'],
#                 "links": row['links'],
#                 "aliases": row['aliases'],
#                 "labels": row['labels'],
#                 "acronyms": row['acronyms'],
#                 "wikipedia_url": row['wikipedia_url'],
#                 "country": row.get('country'),
#                 "state": row.get('state'),
#                 "city": row.get('city')
#             }
#         }
#         actions.append(action)
# # 批量导入数据到Elasticsearch
# helpers.bulk(es, actions)


text = " A Lightweight and Accurate Spatial Temporal Transformer for Traffic Forecasting 1 Guanyao Li Shuhan Zhong S. H. Gary Chan Ruiyuan Li Chih Chieh Hung Wen Chih Peng Abstract We study the forecasting problem for traffic with dynamic possibly periodical and joint spatial temporal dependency between regions. Given the aggregated inflow and outflow traffic of regions in a city from time slots 0 to t − 1 we predict the traffic at time t at any region. Prior arts in the area often consider the spatial and temporal dependencies in a decoupled manner or are rather computationally intensive in training with a large number of hyper parameters to tune. We propose ST TIS a novel lightweight and accurate Spatial Temporal Transformer with information fusion and region sampling for traffic forecasting. ST TIS extends the canonical Transformer with information fusion and region sampling. The information fusion module captures the complex spatial temporal dependency between regions. The region sampling module is to improve the efficiency n) where n is the number of and prediction accuracy cutting the computation complexity for dependency learning from O(n2) to O(n regions. With far fewer parameters than state of the art models ST TIS's offline training is significantly faster in terms of tuning and computation (with a reduction of up to 90% on training time and network parameters). Notwithstanding such training efficiency extensive experiments show that ST TIS is substantially more accurate in online prediction than state of the art approaches (with an average improvement of 9.5% on RMSE and 12.4% on MAPE compared to STDN and DSAN). √ Index Terms spatial temporal forecasting; spatial temporal data mining; efficient Transformer; joint spatial temporal dependency; region sampling. ! 1 INTRODUCTION Traffic forecasting is to predict the inflow (i.e. the number of arriving objects per unit time) and outflow (i.e. the number of departing objects per unit time) of any region in a city at the next time slot. The objects can be people vehicles goods/items etc. Traffic forecasting has important applications in transportation retails public safety city planning etc [1] [2]. For example with traffic forecasting a taxi company may dispatch taxis in a timely manner to meet the supply and demand in different regions of a city. Yet another example is bike sharing where the company may want to balance bike supply and demand at dock stations (regions) based on such forecasting. Although there has been much effort on deep learning to improve the prediction accuracy of the state of the art forecasting models progressive improvements on benchmarks have been correlated with an increase in the number of parameters and the amount of training resources required to train the model making it costly to train and deploy large deep learning models [3]. Therefore a lightweight • Guanyao Li Shuhan Zhong and S. H. Gary Chan are with the Department of Computer Science and Engineering The Hong Kong University of Science and Technology. E mail: {gliaw szhongaj lxiangab gchan}@cse.ust.hk • Ruiyuan Li is with College of Computer Science Chongqing University. • Chih Chieh Hung is with Department of Computer Science and Engineer E mail: liruiyuan@cqu.edu.cn ing National Chung Hsing University. E mail: smalloshin@email.nchu.edu.tw • Wen Chih Peng is with Department of Computer Science National Yang Ming Chiao Tung University. E mail: wcpeng@g2.nctu.edu.tw and training efficient model is essential for fast delivery and deployment. In this work we study the following spatial temporal traffic forecasting problem: Given the historical (aggregated) inflow and outflow data of different regions from time slots 0 to t − 1 (with slot size of say 30 minutes) what is the design of a training efficient model to accurately predict the inflow and outflow of any region at time t? (Note that even though we consider predicting for the next time slot our work can be straightforwardly extended to any future time slot by successive application of the algorithm.) We seek a \"small\" training model with substantially fewer parameters which naturally leads to efficiency in tuning memory and computation time. Despite its training efficiency our lightweight model lightweight it should also achieve higher accuracy than the state of the art approaches in its online predictions. Intuitively region traffic is spatially and temporally correlated. As an example the traffic of a region could be correlated with that of another with some temporal lag due to the travel time between them. Moreover such dependency may be dynamic over different time slots and it may have temporal periodic patterns. This is the case for the traffic of office regions which exhibit high correlation with the residence regions in workday morning but much less than at night or weekend. To accurately predict the region traffic it is hence significantly crucial to account for the dynamic possibly periodical and joint spatial temporal (ST) dependency between regions no matter how far the regions is apart. Much effort has been devoted to capturing the dependency between regions for traffic forecasting. While"
substring = "National Yang Ming Chiao Tung University"

# 将文本和子字符串都转换为小写
text_lower = text.lower()
substring_lower = substring.lower()

# 使用fi# 使用find()方法查找子字符串，不区分大小写nd()方法查找子字符串，不区分大小写
index = text_lower.find(substring_lower)

if index != -1:
    print(f"子字符串 '{substring}' 在文本中的位置是：{index}")
    print(text[index])
else:
    print(f"未找到子字符串 '{substring}'")



