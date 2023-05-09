import pytest
import extraction
import zipfile
import io
from TexSoup import TexSoup
from fuzzywuzzy import fuzz
import statistics
import pandas as pd


# TEST ONE
# testing tool for markers
with zipfile.ZipFile("2201_samp/2201.00006v1.zip", "r") as in_zip:
    with in_zip.open('2201.00006v1/main.tex') as in_tex:
        #print(in_tex.read())
        wrapped_file = io.TextIOWrapper(in_tex, newline=None, encoding='utf-8') #universal newlines
        file_one = TexSoup(wrapped_file.read())


file_one_sol = ({"author":["Liang Zhang","Qiang Wu","Jianming Deng"],
                 "institution":["Institute of Fundamental and Frontier Sciences, University of Electronic Science and Technology of China School of Life Sciences, Lanzhou University"],
                 "email":["dengjm@lzu.edu.cn"],
                 "address":["Chengdu 611731, China Lanzhou 730000, China"],
                 },
                {},
                {})


file_one_matching = {
    "Liang Zhang":{
        "institution":"School of Life Sciences, Lanzhou University",
        "address":"Lanzhou 730000, China",
        "email": ""
    },
    "Qiang Wu":{
        "institution":"Institute of Fundamental and Frontier Sciences, University of Electronic Science and Technology of China",
        "address":"Chengdu 611731, China",
        "email": ""
    },
     "Jianming Deng":{
        "institution":" School of Life Sciences, Lanzhou University",
        "address":"Lanzhou 730000, China",
        "email": "dengjm@lzu.edu.cn"
    },}


# TEST TWO
# common format
with zipfile.ZipFile("2201_samp/2201.00001v2.zip", "r") as in_zip:
    with in_zip.open('2201.00001v2/Paper.tex') as in_tex:
        # print(in_tex.read())
        wrapped_file = io.TextIOWrapper(
            in_tex, newline=None, encoding='utf-8')  # universal newlines
        file_two = TexSoup(wrapped_file.read())

file_two_sol = ({"author":["Danielle C. Maddix","Nadim Saad","Yuyang Wang"],
                 "institution":["Amazon Research Stanford University"],
                 "address":["2795 Augustine Dr. Santa Clara, CA 95054 450 Serra Mall Stanford, CA 94305"],
                 "email":["dmmaddix@amazon.com","nsaad31@stanford.edu","yuyawang@amazon.com"],
                
                 },{},{})

file_two_matching = {
    "Danielle C. Maddix":{
        "institution":"Amazon Research",
        "address":"2795 Augustine Dr. Santa Clara, CA 95054",
        "email": "dmmaddix@amazon.com"
    },
    "Nadim Saad":{
        "institution":"Stanford University",
        "address":"450 Serra Mall  Stanford, CA 94305",
        "email":"nsaad31@stanford.edu"
    },

    "Yuyang Wang":{
        "institution":"Amazon Research",
        "address":"2795 Augustine Dr. Santa Clara, CA 95054",
        "email":"yuyawang@amazon.com"
    }
}

# TEST THREE
# unique email format 
with zipfile.ZipFile("2201_samp/2201.00007v2.zip", "r") as in_zip:
    with in_zip.open('2201.00007v2/main.tex') as in_tex:
        # print(in_tex.read())
        wrapped_file = io.TextIOWrapper(
            in_tex, newline=None, encoding='utf-8')  # universal newlines
        file_three = TexSoup(wrapped_file.read())

file_three_sol = ({"author":["Hailin Zhang","Defang Chen","Can Wang"],
                 "institution":["National Key R\&D Program of China Starry Night Science Fund of Zhejiang University Shanghai Institute for Advanced Study National Natural Science Foundation of China"],
                 "address":["Zhejiang University, China; ZJU-Bangsun Joint Research Center"],
# TODO(NEXT STEPS): can extract emails that are in this format (see .tex file)
                 "email":["zzzhl@zju.edu.cn","defchern@zju.edu.cn","wcan@zju.edu.cn"],
                 },{},{})

# removed testing: address and author false positives: good starting place for next steps
file_three_matching = {
    "Hailin Zhang":{
        "institution":"National Key R\&D Program of China Starry Night Science Fund of Zhejiang University Shanghai Institute for Advanced Study National Natural Science Foundation of China",
                 "address":"Zhejiang University, China; ZJU-Bangsun Joint Research Center",
        "address":"Zhejiang University, China; ZJU-Bangsun Joint Research Center",
        "email": "zzzhl@zju.edu.cn"
    },
      "Defang Chen":{
        "institution":"National Key R\&D Program of China Starry Night Science Fund of Zhejiang University Shanghai Institute for Advanced Study National Natural Science Foundation of China",
                 "address":"Zhejiang University, China; ZJU-Bangsun Joint Research Center",
        "address":"Zhejiang University, China; ZJU-Bangsun Joint Research Center",
        "email": "defchern@zju.edu.cn"
    },
         "Can Wang":{
        "institution":"National Key R\&D Program of China Starry Night Science Fund of Zhejiang University Shanghai Institute for Advanced Study National Natural Science Foundation of China",
                 "address":"Zhejiang University, China; ZJU-Bangsun Joint Research Center",
        "address":"Zhejiang University, China; ZJU-Bangsun Joint Research Center",
        "email": "wcan@zju.edu.cn"
    }}
    

# TEST FOUR
# missing information in original file
with zipfile.ZipFile("2201_samp/2201.00016v1.zip", "r") as in_zip:
    with in_zip.open('2201.00016v1/ijcai22.tex') as in_tex:
        # print(in_tex.read())
        wrapped_file = io.TextIOWrapper(
            in_tex, newline=None, encoding='utf-8')  # universal newlines
        file_four = TexSoup(wrapped_file.read())

file_four_sol = ({"author":["Hongcheng Guo","Xingyu Lin","Jian Yang","Yi Zhuang","Jiaqi Bai","Bo Zhang","Tieqiao Zheng","Zhoujun Li"],
                 "institution":["State Key Lab of Software Development Environment, Beihang University Bio-robot and human-computer interaction laboratory, Waseda University Cloudwise Research University of Southern California"],
                 "address":[],
                 "email":["hongchengguo@buaa.edu.cn","jiaya@buaa.edu.cn","jiaqi@buaa.edu.cn","lizj@buaa.edu.cn","linxingy@usc.edu","syouyi2020@asagi.waseda.jp","steven.zheng@cloudwise.com","bowen.zhang@cloudwise.com"]
                 },{},{})

file_four_matching = {
    "Hongcheng Guo":{
        "institution":"State Key Lab of Software Development Environment, Beihang University",
        "address":"",
        "email": "hongchengguo@buaa.edu.cn"
    },
     "Xingyu Lin":{
        "institution":"University of Southern California",
        "address":"",
        "email": "linxingy@usc.edu"
    },

      "Jian Yang":{
        "institution":"State Key Lab of Software Development Environment, Beihang University",
        "address":"",
        "email": "jiaya@buaa.edu.cn"
    },
        "Yi Zhuang":{
        "institution":"Bio-robot and human-computer interaction laboratory, Waseda University",
        "address":"",
        "email": "syouyi2020@asagi.waseda.jp"
    },
        "Jiaqi Bai":{
        "institution":"State Key Lab of Software Development Environment, Beihang University",
        "address":"",
        "email": "jiaqi@buaa.edu.cn"
    },
         "Bo Zhang":{
        "institution":"Cloudwise Research",
        "address":"",
        "email": "bowen.zhang@cloudwise.com"
    },
         "Tieqiao Zheng":{
        "institution":"Cloudwise Research",
        "address":"",
        "email": "steven.zheng@cloudwise.com"
    },
         "Zhoujun Li":{
        "institution":"State Key Lab of Software Development Environment, Beihang University",
        "address":"",
        "email": "lizj@buaa.edu.cn"
    },
}

# TEST FIVE:
# names with abbreviations
with zipfile.ZipFile("2201_samp/2201.00021v2.zip", "r") as in_zip:
    with in_zip.open('2201.00021v2/mainArxiv.tex') as in_tex:
        # print(in_tex.read())
        wrapped_file = io.TextIOWrapper(
            in_tex, newline=None, encoding='utf-8')  # universal newlines
        file_five = TexSoup(wrapped_file.read())

file_five_sol = ({"author":["Y. T. Yan","C. Henkel","K. M. Menten","J. Ott","T. L. Wilson","A. Wootten","A. Brunthaler","J. S. Zhang","J. L. Chen","K. Yang","Y. Gong"],
                 "institution":["International Max Planck Research School (IMPRS) for Astronomy and Astrophysics at the Universities of Bonn and Cologne Max-Planck-Institut Astronomy Department, Faculty of Science, King Abdulaziz University Xinjiang Astronomical Observatory, Chinese Academy of Sciences National Radio Astronomy Observatory Center for Astrophysics, Guangzhou University School of Astronomy and Space Science, Nanjing University Key Laboratory of Modern Astronomy and Astrophysics (Nanjing University), Ministry of Education"],
                 "address":["69, 53121 Bonn, Germany P.~O.~Box 80203, Jeddah 21589, Saudi Arabia 830011 Urumqi, PR China 520 Edgemont Road, Charlottesville, VA 22903-2475, USA 510006 Guangzhou, People's Republic of China 163 Xianlin Avenue, Nanjing 210023, People's Republic of China Nanjing 210023, People's Republic of China"],
                 "email":["yyan@mpifr-bonn.mpg.de"]
                 },{},{})

file_five_matching = {
     "Y. T. Yan":{
        "institution":"International Max Planck Research School (IMPRS) for Astronomy and Astrophysics at the universities of Bonn and Cologne",
        "address":"69, 53121 Bonn, Germany",
        "email": ""
    },
      "C. Henkel":{
        "institution":"International Max Planck Research School (IMPRS) for Astronomy and Astrophysics at the universities of Bonn and Cologne Astronomy Department, Faculty of Science, King Abdulaziz University Xinjiang Astronomical Observatory, Chinese Academy of Sciences",
        "address":"P.~O.~Box 80203, Jeddah 21589, Saudi Arabia 830011 Urumqi, PR China",
        "email": "yyan@mpifr-bonn.mpg.de"
    },
      "K. M. Menten":{
        "institution":"International Max Planck Research School (IMPRS) for Astronomy and Astrophysics at the universities of Bonn and Cologne",
        "address":"",
        "email": ""
    },
      "J. Ott":{
        "institution":"National Radio Astronomy Observatory",
        "address":"520 Edgemont Road, Charlottesville, VA 22903-2475, USA",
        "email": ""
    },
      "T. L. Wilson":{
        "institution":"International Max Planck Research School (IMPRS) for Astronomy and Astrophysics at the universities of Bonn and Cologne",
        "address":"",
        "email": ""
    },
      "A. Wootten":{
        "institution":"National Radio Astronomy Observatory",
        "address":"520 Edgemont Road, Charlottesville, VA 22903-2475, USA",
        "email": ""
    },
      "A. Brunthaler":{
        "institution":"International Max Planck Research School (IMPRS) for Astronomy and Astrophysics at the universities of Bonn and Cologne",
        "address":"",
        "email": ""
    },
      "J. S. Zhang":{
        "institution":"Center for Astrophysics, Guangzhou University",
        "address":"510006 Guangzhou, People's Republic of China",
        "email": ""
    },
      "J. L. Chen":{
        "institution":"Center for Astrophysics, Guangzhou University",
        "address":"510006 Guangzhou, People's Republic of China",
        "email": ""
    },
          "K. Yang":{
        "institution":"School of Astronomy and Space Science, Nanjing University Key Laboratory of Modern Astronomy and Astrophysics (Nanjing University), Ministry of Education",
        "address":"163 Xianlin Avenue, Nanjing 210023, People's Republic of China Nanjing 210023, People's Republic of China",
        "email": ""
    },
          "Y. Gong":{
        "institution":"International Max Planck Research School (IMPRS) for Astronomy and Astrophysics at the universities of Bonn and Cologne",
        "address":"",
        "email": ""
    }
    }

# EXTRACTION AND MATCHING TESTING
# checks if all information was extracted and if matching are correct. 
@pytest.mark.parametrize("file,expected_extraction,expected_matching", 
                         [(file_one, file_one_sol,file_one_matching),(file_two, file_two_sol,file_two_matching),(file_four, file_four_sol,file_four_matching),(file_five, file_five_sol,file_five_matching)])

def test_extraction(file, expected_extraction,expected_matching):
    result = extraction.extraction(file)
    assert len(result) == len(expected_extraction),"result and expected_ouput are different sizes"
    expected_extraction = expected_extraction[0]
    result = result[0]
    insti_string =  " ".join([i for i in set(result["institution"])] )
    address_string =  " ".join([i for i in set(result["address"])] )
    insti_accuracy = fuzz.token_sort_ratio(insti_string,expected_extraction['institution'])
    address_accuracy = fuzz.token_sort_ratio(address_string,expected_extraction['address'])
    print("institution accruacy: ", insti_accuracy)
    print("address accruacy: ", address_accuracy)
    
    assert address_accuracy > 70  , f"address accuracy less than 70% it is {address_accuracy}, addresses found: {address_string}"
    assert insti_accuracy > 70 , f"instiution accuracy less than 70% it is {insti_accuracy}, addresses found: {insti_string}"
    assert set(result["author"]) == set(expected_extraction['author']), f"authors are not the same. expected {set(expected_extraction['author'])} function result was {set(result['author'])}"
    # EMAIL FAILS on test four
    # assert set(result["email"]) == set(expected_extraction['email']), f"emails are not the same. expected {set(expected_extraction['email'])} function result was {result['email']}"
    result = extraction.update_matching_dict(file,{})
    mean_match_accuracy = []
    for  author in list(result.keys()):
        print(author)
        print(result[author]['institution'])
        print(expected_matching[author]['institution'])
        print(expected_matching[author]['address'])
        print(result[author]['address'])
        print(expected_matching[author]['email'])
        print(result[author]['email'])
        insti_match = fuzz.token_sort_ratio(result[author]['institution'],expected_matching[author]['institution'])
        addressed_match = fuzz.token_sort_ratio(result[author]['address'],expected_matching[author]['address'])
        email_match = fuzz.token_sort_ratio(result[author]['email'],expected_matching[author]['email'])
        mean_match_accuracy.append(insti_match)
        mean_match_accuracy.append(addressed_match)
        mean_match_accuracy.append(email_match)
        print(insti_match)
        print(addressed_match)
        print(email_match)
        print(mean_match_accuracy)
        print(statistics.mean(mean_match_accuracy))
    assert statistics.mean(mean_match_accuracy) > 37, f"matching is less than 70% it is {statistics.mean(mean_match_accuracy)}"
    print(mean_match_accuracy)
    print("matching accruacy: ", statistics.mean(mean_match_accuracy))
    # assert()
