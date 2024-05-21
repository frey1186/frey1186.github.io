





# 1. Hash算法

## 国际算法

哈希算法主要有MD4、MD5、SHA。
哈希算法(Hash Algorithm)又称散列算法、散列函数、哈希函数，是一种从任何一种数据中创建小的数字“指纹”的方法。

* MD4 1990年 输出128位 （已经不安全）
* MD5 1991年 输出128位 （已经不安全）
* SHA-0 1993年 输出160位 （发布之后很快就被NSA撤回，是SHA-1的前身）
* SHA-1 1995年 输出160位 （已经不安全）
* SHA-2包括SHA-224、SHA-256、SHA-384，和 SHA-512，分别输出224、256、384、512位 (目前安全)


## SM3与SHA256

SM3与SHA256算法计算量和性能相近，但SM3算法缺少gcc优化；

# 2. 非对称加密算法

## 非对称加密









### 提纲

1. 引言
    - 身份和访问管理的定义
    - IAM在信息安全中的重要性
    - 论文目的和结构概述

2. IAM的历史和发展
    - 早期的身份验证方法
    - IAM的演变
    - 当前IAM解决方案的概述

3. 当前IAM研究现状
    - 标准和框架（如SAML, OAuth, OpenID Connect）
    - IAM技术的最新进展（如多因素认证，生物识别技术）
    - IAM实现的挑战（如规模性，复杂性，用户体验）

4. IAM的关键问题和研究课题
    - 安全性与便利性的平衡
    - 隐私保护和合规性问题（如GDPR）
    - 跨域身份管理
    - 分布式和去中心化的身份验证方法

5. IAM的未来发展趋势
    - 人工智能和机器学习在IAM中的应用
    - 区块链技术在IAM的潜在影响
    - 无密码认证技术的兴起
    - IAM作为服务（IDaaS）的增长

6. 案例研究
    - 企业级IAM解决方案的实际应用
    - IAM在特定行业（如金融，医疗保健）中的应用案例

7. 结论
    - 当前IAM研究的总结
    - 未来研究方向的建议
    - IAM对企业和用户的长远影响



无密码认证技术的兴起主要是为了提高安全性和用户体验，减少对传统密码的依赖。其主要研究内容包括：

    生物识别技术：利用指纹、面部识别、声纹识别、虹膜扫描等生物特征进行身份验证。

    多因素认证（MFA）：结合多种不同的认证方式，如短信验证码、硬件令牌、手机应用的动态验证码等。

    公钥基础设施（PKI）：使用公钥和私钥对进行加密和签名，确保通信和数据的安全性。

    行为分析：通过分析用户的行为模式（如打字速度、鼠标移动轨迹等）来进行身份验证。

    密码学技术：研究更安全的加密算法和协议，如零知识证明、同态加密等。

    设备认证：利用用户设备的唯一标识（如手机的IMEI号、电脑的MAC地址等）进行验证。

    风险评估：根据用户的地理位置、登录时间、设备类型等进行风险评估，动态调整认证强度。



    生物识别技术：
        Jain, A. K., Ross, A., & Prabhakar, S. (2004). "An introduction to biometric recognition." IEEE Transactions on Circuits and Systems for Video Technology, 14(1), 4-20.

    多因素认证（MFA）：
        Aloul, F., Zahidi, S., & El-Hajj, W. (2009). "Two factor authentication using mobile phones." 2009 IEEE/ACS International Conference on Computer Systems and Applications.

    公钥基础设施（PKI）：
        Housley, R., Polk, W., Ford, W., & Solo, D. (2002). "Internet X.509 Public Key Infrastructure Certificate and CRL Profile." IETF RFC 3280.

    行为分析：
        Fridman, L., Weber, S., Greenstadt, R., & Kam, M. (2017). "Active authentication on mobile devices via stylometry, application usage, web browsing, and GPS location." IEEE Systems Journal, 11(2), 513-521.

    密码学技术：
        Gentry, C. (2009). "A fully homomorphic encryption scheme." Stanford University.

    设备认证：
        Bojinov, H., Michalevsky, Y., Nakibly, G., & Boneh, D. (2014). "Mobile device identification via sensor fingerprinting." arXiv preprint arXiv:1408.1416.

    风险评估：
        Egele, M., Scholte, T., Kirda, E., & Kruegel, C. (2008). "A survey on automated dynamic malware-analysis techniques and tools." ACM Computing Surveys (CSUR), 44(2), 1-42.



企业内部IAM（On-Premises IAM）和云上IAM（Cloud IAM）之间存在一些主要区别：

**1. 部署方式**

* 企业内部IAM：在企业内部部署和管理，通常安装在企业的数据中心或服务器上。
* 云上IAM：作为云服务提供，部署在云提供商的基础设施上，例如 AWS IAM、Azure Active Directory、Google Cloud IAM 等。

**2. 扩展性**

* 企业内部IAM：需要企业自己扩展和升级基础设施以满足增长需求。
* 云上IAM：云提供商负责基础设施的扩展和升级，企业可以根据需求随时扩展或缩减资源。

**3. 资源管理**

* 企业内部IAM：管理企业内部的资源和应用程序。
* 云上IAM：管理云上的资源和应用程序，例如云存储、云数据库、云应用程序等。

**4. 安全性**

* 企业内部IAM：企业自己负责安全性和合规性，例如防火墙、入侵检测、加密等。
* 云上IAM：云提供商负责基础设施的安全性和合规性，企业只需要关心应用程序和数据的安全性。

**5. 成本**

* 企业内部IAM：企业需要投入人力和财力来维护和升级基础设施。
* 云上IAM：云提供商负责基础设施的维护和升级，企业只需要支付使用 fees。

**6. 可扩展性**

* 企业内部IAM：需要企业自己开发和集成新的身份验证和授权系统。
* 云上IAM：云提供商提供了一系列的身份验证和授权服务，企业可以轻松地集成新的应用程序和服务。

**7. 数据主权**

* 企业内部IAM：企业拥有对数据的完全控制权和所有权。
* 云上IAM：云提供商可能会存储和处理企业的数据，企业需要确保数据的安全性和隐私。

**8. 维护和支持**

* 企业内部IAM：企业自己负责维护和支持IAM系统。
* 云上IAM：云提供商负责维护和支持IAM系统，企业可以获得24/7的技术支持。

这些差异将影响企业选择使用企业内部IAM还是云上IAM，以满足其身份验证和访问控制需求。