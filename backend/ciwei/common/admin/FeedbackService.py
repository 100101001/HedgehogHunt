# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/4/30 下午4:54
@file: FeedbackService.py
@desc: 
"""
from common.admin.decorators import user_op
from common.libs.MemberService import MemberService
from common.libs.UploadService import UploadService
from common.models.ciwei.Feedback import Feedback
from common.search.decorators import db_search


class FeedbackHandler:
    __strategy_map = {
        'init': '_initFeedback',
        'addImage': '_addImage',
        'search': '_getFeedback',
        'delOrRead': '_delOrReadFeedbacks'
    }

    @classmethod
    def deal(cls, op='', **kwargs):
        strategy = cls.__strategy_map.get(op)
        handler = getattr(cls, strategy, None)
        if handler:
            return handler(**kwargs)

    @classmethod
    def _initFeedback(cls, author_info=None, summary='', has_img=0, **kwargs):
        feedback = Feedback(author_info=author_info, summary=summary, has_img=has_img)
        # 反馈成功，用户积分涨5
        MemberService.updateCredits(member_id=author_info.id)
        return feedback

    @classmethod
    def _addImage(cls, total=0, feedback_id=0, image=None, **kwargs):
        feedback = Feedback.query.filter_by(id=feedback_id).with_for_update().first()
        if not feedback:
            return False
        # 保存图片到数据库和文件系统
        # 在反馈的pics中加入图片路径: 日期/文件名
        ret = UploadService.uploadByFile(image)
        if ret['code'] != 200:
            return False
        pic_url = ret['data']['file_key']
        feedback.addImage(pic=pic_url, total=total)
        return True

    @classmethod
    @user_op
    @db_search(out_num=2)
    def _getFeedback(cls, user=None,  **kwargs):
        """
        用来判断user是否已经读过反馈
        :param user:
        :param kwargs:
        :return:
        """
        return Feedback.query.filter_by(status=1), str(user.uid)

    @staticmethod
    @user_op
    def _delOrReadFeedbacks(del_ids=None, read_ids=None, user=None, **kwargs):
        user_id = user.uid
        if read_ids:
            Feedback.query.filter(Feedback.id.in_(read_ids)).update({'views': str(user_id) if not Feedback.views else
            Feedback.views + (',{}'.format(user_id))}, synchronize_session=False)
        if user.level == 1 and del_ids:
            Feedback.query.filter(Feedback.id.in_(del_ids), Feedback.status == 0).update({'status': 7},
                                                                                         synchronize_session=False)
        return True, ''
